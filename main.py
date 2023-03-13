from threading import Thread
from queue import Queue
import serial
from pathfinding import *

segmentationQueue = queue.Queue()
pathfindingQueue = queue.Queue()
serialToMotor = serial.Serial('port')

###################################################
##      THREAD 1 : CHARACTER PREPROCESSING       ##

# When letter recieved:
#   Do skeletonization
#   Add output to segmentation queue


###################################################
##      THREAD 2 : CHARACTER SEGMENTATION        ##

while not segmentationQueue.empty():
    # Take next letter from segmentation queue
    # Perform character segmentation
    # Add output list of lines to pathfinding queue

###################################################
##      THREAD 3 : PATHFINDING                   ##

while True:
    while not pathfindingQueue.empty():
        lines = pathfindingQueue.get()
        pathfinder = Pathfinder(lines)
        pathfinder.pathfind()
        pathfinder.convert()
        serialToMotor(pathfinder.getGCode())
