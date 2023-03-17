from threading import Thread
from queue import Queue
import serial
from pathfinding import *

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
