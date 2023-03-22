from threading import Thread
from queue import Queue
import sys
import serial
import time
from character_segmentation import *
from CharacterCache import *
sys.path.insert(0, './pathfinding')
from pathfinding import *
from SpaceCadet import *

###################################################
##      THREAD 1 : CHARACTER PREPROCESSING       ##

def charPreProcProcess():

    ### TEST CODE ###

    while True:
        for i in range(6):
            segmentationQueue.put(i)
            time.sleep(1)

    #################

    print("Placeholder")
#   When letter recieved:
#       Check if letter is in character cache
#       Do skeletonization
#       Add output to segmentation queue

###################################################
##      THREAD 2 : CHARACTER SEGMENTATION        ##

def segmentationProcess():

    ### TEST CODE ###

    while True:
        while not segmentationQueue.empty():
            tgt = segmentationQueue.get()
            lines = []
            if tgt == 0: # Square
                lines.append(Line(.199,.2,.2,.4))
                lines.append(Line(.4,.2,.2,.2))
                lines.append(Line(.2,.4,.4,.4001))
                lines.append(Line(.4,.4,.4,.2))
            elif tgt == 1: # Circles
                lines.append(Line(.3,.2,.2,.1,.2,.2,90))
                lines.append(Line(.1,.2,.2,.3,.2,.2,90))
                lines.append(Line(.2,.3,.3,.2,.2,.2,90))
                lines.append(Line(.2,.1,.1,.2,.2,.2,90))
                lines.append(Line(.5,.4,.4,.3,.4,.4,90))
                lines.append(Line(.3,.4,.4,.5,.4,.4,90))
                lines.append(Line(.4,.5,.5,.4,.4,.4,90))
                lines.append(Line(.4,.3,.3,.4,.4,.4,90))
            elif tgt == 2: # Semicircle
                lines.append(Line(.1,.2,.2,.1,.2,.2,90))
                lines.append(Line(.2,.1,.3,.2,.2,.2,90))
                lines.append(Line(.3,.2,.1,.2))
            elif tgt == 3: # Arcs
                lines.append(Line(.1,.3,.2,.4,.2,.3,90))
                lines.append(Line(.2,.4,.3,.3,.2,.3,90))
                lines.append(Line(.3,.2,.2,.3,.2,.2,90))
                lines.append(Line(.2,.3,.1,.2,.2,.2,90))
            elif tgt == 4: # Circle+Square
                lines.append(Line(.2,.2,.2,.4))
                lines.append(Line(.4,.2,.2,.2))
                lines.append(Line(.2,.4,.4,.4))
                lines.append(Line(.4,.4,.4,.2))
                lines.append(Line(.5,.4,.4,.3,.4,.4,90))
                lines.append(Line(.3,.4,.4,.5,.4,.4,90))
                lines.append(Line(.4,.5,.5,.4,.4,.4,90))
                lines.append(Line(.4,.3,.3,.4,.4,.4,90))
            elif tgt == 5: # L
                lines.append(Line(628.234,1427.96,929,1427.96))
                lines.append(Line(563.456,1376.21,563.456,876.21))
                lines.append(Line(563.456,1376.21,628.234,1427.96,626,1364,51.75))
            pack = PathfindingPackage(lines,str(tgt),"Font")
            pathfindingQueue.put(pack)

    #################

    while True:
        while not segmentationQueue.empty():
            img = segmentationQueue.get()
            line_segments = find_lines(img)
            # centers, radii, votes = find_circles(img, range(20,100,5), 0.6, 20)
            # good_circles = np.logical_and(votes > 0.6 * np.max(votes), votes > np.array([60])[0])
            # centers = centers[np.squeeze(good_circles)]
            # radii = radii[good_circles]
            # votes = np.take(votes, np.where(good_circles))[0]
            # arc_list = find_arcs(centers, radii, votes, img)

            segment_list = []
            # Line(self,startX,startY,endX,endY,centerX=-1,centerY=-1,arc=0):
            for line in line_segments:
                x1, y1 = line[0]
                x2, y2 = line[1]
                segment_list.append(Line(x1,y1,x2,y2,-1,-1,0))

            # for arc in arc_list:
            #     cx, cy, r, start_angle, end_angle, start_idx, end_idx = arc
            #     segment_list.append(Line(x1,y1,x2,y2,-1,-1,0))

            pathfindingQueue.put(segment_list)
#           Take next letter from segmentation queue
#           Perform character segmentation
#           Add output list of lines to pathfinding queue

###################################################
##      THREAD 3 : PATHFINDING                   ##

def pathfindingProcess():
    spacer = SpaceCadet(1)
    while True:
        while not pathfindingQueue.empty():
            package = pathfindingQueue.get()
            lines = package.lines
            if lines == "Dummy":
                lines == cacheQueue.get()
            pathfinder = Pathfinder(lines)
            pathfinder.pathfind()
            pathfinder.convert(spacer)
            serialQueue.put(pathfinder.getGCode())
            spacer.step()

###################################################
##      THREAD 4 : SERIAL                        ##

def serialProcess():
    while True:
        while not serialQueue.empty():
            gcode = serialQueue.get()
            for line in gcode.splitlines():
                line = line.strip()
                print(f'Sending: {line}')
                serialToMotor.write(str.encode(line + '\n'))
                ack = serialToMotor.readline()
                print(f' : {ack.strip()}')

####################################################

charPreProcThread = Thread(target=charPreProcProcess)
segmentationThread = Thread(target=segmentationProcess)
pathfindingThread = Thread(target=pathfindingProcess)
serialThread = Thread(target=serialProcess)

segmentationQueue = Queue()
pathfindingQueue = Queue()
serialQueue = Queue()
cacheQueue = Queue()

serialToMotor = serial.Serial('COM3')
serialToMotor.write(str.encode("\r\n\r\n"))
time.sleep(2)   # Wait for grbl to initialize
serialToMotor.flushInput()  # Flush startup text in serial input

charPreProcThread.start()
segmentationThread.start()
pathfindingThread.start()
serialThread.start()