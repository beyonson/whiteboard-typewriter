from threading import Thread
from queue import Queue
import sys
import serial
import time
sys.path.insert(0, './character_segmentation')
from segmentation import get_image, find_lines, find_arcs, find_circles, circle_processing, remove_overlap_lines, remove_intersections, find_lind_idx
from CharacterCache import *
sys.path.insert(0, './pathfinding')
from pathfinding import *
from SpaceCadet import *
import math

charCache = CharacterCache(26)


def segmentationProcess(tgt):

    # run segmentation on current file path
    print(tgt[0])

    if tgt[1] == '^': # Placeholder character representing a reset
        pack = PathfindingPackage("",str(tgt[1]),"Font","Reset")
        return pack
    if tgt[1] == '>': # Placeholder character representing a new line
        pack = PathfindingPackage("",str(tgt[1]),"Font","Return")
        return pack
    if tgt[1] == '_':
        pack = PathfindingPackage("",str(tgt[1]),"Font","Space")
        return pack
    out = charCache.poll(tgt[1]) # Out is the collection of segments, not gcode, because the spacer still needs to determine where the letter will be drawn
    if out != "":
        pack = PathfindingPackage(out,str(tgt[1]),"Font","Cached")
        return pack

    img = get_image(tgt[0])

    path_finding_lines = []

    line_segments = find_lines(img, rho=1, theta=math.pi/180, threshold=12, minLineLength=1, maxLineGap=10)
    # line_segments = find_lines(img, rho=1, theta=math.pi/180, threshold=13, minLineLength=1, maxLineGap=10)


    line_segments = remove_intersections(line_segments)

    # line_idx = find_lind_idx(line_segments)

    # centers, radii, votes = find_circles(img, range(20,500,5), 0.70, 30, line_idx)

    # centers, radii, votes = circle_processing(centers, radii, votes, 0.7, 10)

    arc_list = []
    # arc_list = find_arcs(centers, radii, votes, img)

    # line_segments = remove_overlap_lines(line_segments, arc_list, 0.25, 2)

    print("Finished segments")

    for i in range(len(line_segments)):
        # class Line:
        # def __init__(self,startX,startY,endX,endY,centerX=-1,centerY=-1,arc=0):
        path_finding_lines.append(Line(line_segments[i][0][0], line_segments[i][0][1], line_segments[i][1][0], line_segments[i][1][1]))

    for i in range(len(arc_list)):
        if (arc_list[i][3] - arc_list[i][2]) < 180:
            path_finding_lines.append(Line(arc_list[i][4][0], arc_list[i][4][1], arc_list[i][5][0], arc_list[i][5][1], arc_list[i][0][0], arc_list[i][0][1],(arc_list[i][3]-arc_list[i][2])))
        else:
            path_finding_lines.append(Line(arc_list[i][4][1], arc_list[i][4][0], arc_list[i][5][1], arc_list[i][5][0], arc_list[i][0][0], arc_list[i][0][1],(arc_list[i][2]-arc_list[i][3])))



    pack = PathfindingPackage(path_finding_lines,str(tgt[1]),"Font")

    return pack


def pathfindingProcess(pack,spacer):
    lines = pack.lines
    print(f'Lines: {len(lines)}')
    pathfinder = Pathfinder(lines,.025)
    if pack.type == "Cached":
        gcode = pathfinder.convert(spacer)
        spacer.step()
        return pathfinder.getGCode()
    elif pack.type == "Reset":
        spacer.reset()
        return "G01 X" + str(spacer.plot((0,0))[0]) + " Y" + str(spacer.plot((0,0))[1]) + " Z0\n"
    elif pack.type == "Return":
        spacer.nextLine()
        return "G01 X" + str(spacer.plot((0,0))[0]) + " Y" + str(spacer.plot((0,0))[1]) + " Z0\n"
    elif pack.type == "Space":
        spacer.step()
        return "G01 X" + str(spacer.plot((0,0))[0]) + " Y" + str(spacer.plot((0,0))[1]) + " Z0\n"
    pathfinder.setVerbosity(False)
    pathfinder.setRipcord(5)
    pathfinder.pathfind()
    pathfinder.convert(spacer)
    gcode = pathfinder.getGCode()
    spacer.step()
    charCache.add(pack.letter,pathfinder.segments)

    return gcode

def serialProcess(gcode, serialToMotor):
    start = time.time()
    for line in gcode.splitlines():
        line = line.strip()
        print(f'Sending: {line}')
        serialToMotor.write(str.encode(line + '\n'))
        ack = serialToMotor.readline()
        print(f' : {ack.strip()}')
    return time.time() - start

def serialInit(serialToMotor):
    print("IN")
    serialToMotor = serial.Serial('COM3') # /dev/ttyACM0
    serialToMotor.write(str.encode("\r\n\r\n"))
    time.sleep(2)   # Wait for grbl to initialize
    serialToMotor.flushInput()  # Flush startup text in serial input
    serialToMotor.write(str.encode("$$\n$1 = 25    (step idle delay, msec)\n$0 = 10    (step pulse, usec)\n$2 = 0    (step port invert mask:00000000)\n$3 = 0    (dir port invert mask:00000000)\n$4 = 0    (step enable invert, bool)\n$5 = 0    (limit pins invert, bool)\n$6 = 0    (probe pin invert, bool)\n$10 = 1    (status report mask:00000001)\n$11 = 0.010    (junction deviation, mm)\n$12 = 0.002    (arc tolerance, mm)\n$20 = 0    (soft limits, bool)\n$13 = 0    (report inches, bool)\n$21 = 0    (hard limits, bool)\n$22 = 1    (homing cycle, bool)\n$23 = 3    (homing dir invert mask:00000011)\n$24 = 25.000    (homing feed, mm/min)\n$25 = 50.000    (homing seek, mm/min)\n$26 = 250    (homing debounce, msec)\n$27 = 1.000    (homing pull-off, mm)\n$100 = 250.000    (x, step/mm)\n$101 = 250.000    (y, step/mm)\n$102 = 250.000    (z, step/mm)\n$110 = 500.000    (x max rate, mm/min)\n$111 = 500.000    (y max rate, mm/min)\n$112 = 500.000    (z max rate, mm/min)\n$120 = 10.000    (x accel, mm/sec^2)\n$121 = 10.000    (y accel, mm/sec^2)\n$122 = 10.000    (z accel, mm/sec^2)\n$130 = 20000.000    (x max travel, mm)\n$131 = 20000.000    (y max travel, mm)\n$132 = 200.000    (z max travel, mm)"))
    ack = serialToMotor.readline()
    print(f' : {ack.strip()}')
    serialToMotor.write(str.encode("$G"))
    serialToMotor.write(str.encode("$H"))

if __name__ == "__main__":

    currentText = ""
    textfile = open("typedText.txt", "r+")
    spacer = SpaceCadet(3)

    if (len(sys.argv) > 2):
        print("ERROR: too many args")
        exit
    elif (len(sys.argv) == 2):
        serialFlag = True
    else:
        serialFlag = False

    serialToMotor = ''
    if serialFlag:
        serialInit(serialToMotor)

    # check to see if text has changed
    while(True):
        updatedText = textfile.readline()
        if (updatedText != currentText):
            # if text is changed, send to yasser and update
            for i in range(len(currentText), len(updatedText)-1):
                asciiNum = ord(updatedText[i])
                # filename = "font-loader/chars/myfile" + str(asciiNum) + ".bmp"
                filename = "character_segmentation/prototyping/chars/myfile" + str(asciiNum) + ".bmp"
                segInfo = [filename, chr(asciiNum)]

                startSeg = time.time()
                print(updatedText[i])
                lines = segmentationProcess(segInfo)
                endSeg = time.time()
                gcode = pathfindingProcess(lines,spacer)
                print(f'Time elapsed - Segmentation: {endSeg-startSeg}, Pathfinding: {time.time()-endSeg}')
                print(gcode)
                gantryTime = "N/A"
                if serialFlag:
                    gantryTime = serialProcess(gcode, serialToMotor)
                print(f'Time elapsed for gantry: {gantryTime}')
                print('\n')

            currentText = updatedText
