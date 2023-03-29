from threading import Thread
from queue import Queue
import sys
import serial
import time
sys.path.insert(0, './character_segmentation')
from segmentation import get_image, find_lines, find_arcs, find_circles, circle_processing, remove_overlap_lines
from CharacterCache import *
sys.path.insert(0, './pathfinding')
from pathfinding import *
from SpaceCadet import *

###################################################
##      THREAD 1 : CHARACTER PREPROCESSING       ##


def charPreProcProcess():

    currentText = ""

    # open text file
    textfile = open("typedText.txt", "r+")
    updatedText = textfile.readline()

    # check to see if text has changed
    if (updatedText != currentText):
        # if text is changed, send to yasser and update
        for i in range(len(currentText), len(updatedText)-1):
            asciiNum = ord(updatedText[i])
            filename = "opengl-text-editor/chars/myfile" + str(asciiNum) + ".bmp"
            segInfo = [filename, chr(asciiNum)]
            print(segInfo)

            return segInfo
        
        currentText = updatedText



def segmentationProcess(tgt):

    # run segmentation on current file path
    print(tgt[0])
    img = get_image(tgt[0])

    path_finding_lines = []

    line_segments = find_lines(img)

    centers, radii, votes = find_circles(img, range(20,100,5), 0.6, 20)

    centers, radii, votes = circle_processing(centers, radii, votes)

    arc_list = find_arcs(centers, radii, votes, img)

    line_segments = remove_overlap_lines(line_segments, arc_list)

    print("Finished segments")

    for i in range(len(line_segments)):
        # class Line:
        # def __init__(self,startX,startY,endX,endY,centerX=-1,centerY=-1,arc=0):
        path_finding_lines.append(Line(line_segments[i][0][0], line_segments[i][0][1], line_segments[i][1][0], line_segments[i][1][1]))


    pack = PathfindingPackage(path_finding_lines,str(tgt[1]),"Font")

    return pack


def pathfindingProcess(pack):
    spacer = SpaceCadet(1)

    package = pack
    lines = package.lines
    # if package.letter == "Dummy":
    #     lines == cacheQueue.get()
    pathfinder = Pathfinder(lines)
    pathfinder.pathfind()
    pathfinder.convert(spacer)
    gcode = pathfinder.getGCode()
    spacer.step()

    return gcode

def serialProcess(gcode):
    for line in gcode.splitlines():
        line = line.strip()
        print(f'Sending: {line}')
        serialToMotor.write(str.encode(line s+ '\n'))
        ack = serialToMotor.readline()
        print(f' : {ack.strip()}')


if __name__ == "__main__":

    currentText = ""
    textfile = open("typedText.txt", "r+")
    updatedText = textfile.readline()

    # check to see if text has changed
    if (updatedText != currentText):
        # if text is changed, send to yasser and update
        for i in range(len(currentText), len(updatedText)-1):
            asciiNum = ord(updatedText[i])
            filename = "opengl-text-editor/chars/myfile" + str(asciiNum) + ".bmp"
            segInfo = [filename, chr(asciiNum)]

            lines = segmentationProcess(segInfo)
            gcode = pathfindingProcess(lines)
            serialProcess(gcode)

        currentText = updatedText




