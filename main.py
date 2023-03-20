from threading import Thread
from queue import Queue
import serial
from pathfinding import *
from character_segmentation import *

charPreProcThread = Thread(target=charPreProcProcess, args(1,))
segmentationThread = Thread(target=segmentationProcess, args(2,))
pathfindingThread = Thread(target=pathfindingProcess, args(3,))

segmentationQueue = queue.Queue()
pathfindingQueue = queue.Queue()
serialToMotor = serial.Serial('COM3')

charPreProcThread.start()
segmentationThread.start()
pathfindingThread.start()

###################################################
##      THREAD 1 : CHARACTER PREPROCESSING       ##

def charPreProcProcess():
#   When letter recieved:
#       Do skeletonization
#       Add output to segmentation queue


###################################################
##      THREAD 2 : CHARACTER SEGMENTATION        ##

def segmentationProcess():
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
    while True:
        while not pathfindingQueue.empty():
            lines = pathfindingQueue.get()
            pathfinder = Pathfinder(lines)
            pathfinder.pathfind()
            pathfinder.convert()
            serialToMotor.write(pathfinder.getGCode())
