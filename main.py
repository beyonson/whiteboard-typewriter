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


def segmentationProcess(tgt):

    # run segmentation on current file path
    print(tgt[0])
    img = get_image(tgt[0])

    path_finding_lines = []

    line_segments = find_lines(img, rho=1, theta=math.pi/180, threshold=13, minLineLength=1, maxLineGap=10)
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

    package = pack
    lines = package.lines
    print(f'Lines: {len(lines)}')
    # if package.letter == "Dummy":
    #     lines == cacheQueue.get()
    pathfinder = Pathfinder(lines,.025)
    pathfinder.setVerbosity(False)
    pathfinder.setRipcord(5)
    pathfinder.pathfind()
    pathfinder.convert(spacer)
    gcode = pathfinder.getGCode()

    return gcode

def serialProcess(gcode, serialToMotor):
    for line in gcode.splitlines():
        line = line.strip()
        print(f'Sending: {line}')
        serialToMotor.write(str.encode(line + '\n'))
        ack = serialToMotor.readline()
        print(f' : {ack.strip()}')


if __name__ == "__main__":

    currentText = ""
    textfile = open("typedText.txt", "r+")
    updatedText = textfile.readline()
    spacer = SpaceCadet(1)

    if (len(sys.argv) > 2):
        print("ERROR: too many args")
        exit
    elif (len(sys.argv) == 2):
        serialFlag = True
    else:
        serialFlag = False

    serialToMotor = ''
    if serialFlag:
        serialToMotor = serial.Serial('COM3') # /dev/ttyACM0

    # check to see if text has changed
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
            spacer.step()
            print(f'Time elapsed - Segmentation: {endSeg-startSeg}, Pathfinding: {time.time()-endSeg}')
            print(gcode)
            if serialFlag:
                serialProcess(gcode, serialToMotor)
            print('\n')

        currentText = updatedText
