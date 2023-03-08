# g-code Commands
#
# G01 X# Y# Z# F#: Draws a straight line to (X, Y) at F speed. Z=0 means marker is up. Z=1 means marker is down.
# G02 X# Y# Z# I# J# F#: Draws a curved line to (X, Y) at F speed, rotating clockwise about (I, J). Z=0 means marker is up. Z=1 means marker is down.
# G03 X# Y# Z# I# J# F#: Draws a curved line to (X, Y) at F speed, rotating counter-clockwise about (I, J). Z=0 means marker is up. Z=1 means marker is down.
# G17: Write on XY plane
# G20: Set units to inches
# G21: Set units to millimeters
# G28: Return home

import math

class Line:
    def __init__(self,startX,startY,endX,endY,centerX=-1,centerY=-1,arc=0):
        self.start = (startX,startY)
        self.end = (endX,endY)
        self.center = (centerX,centerY)
        self.arc = arc # In Degrees
    def getRelative(self):
        return (self.end[0]-self.start[0],self.end[1]-self.start[1])
    def getRelativeOf(self,relPoint):
        return (relPoint[0]-self.start[0],relPoint[1]-self.start[1])
    def checkPickup(self,lastPoint):
        return lastPoint != self.start
    def checkDirection(self): # T = CW, F = CCW
        # Check if C is above or below line
        slope = (self.end[1] - self.start[1]) / (self.end[0] - self.start[0])
        yint = self.start[1] - (slope * self.start[0])
        centerOnLine = (self.center[0] * slope) + yint # TODO: Make sure this works when Start and End points are flipped!!
        if self.start[0] < self.end[0]:
            if centerOnLine < self.center[1]:
                return self.arc > 180
            else:
                return self.arc < 180
        else:
            if centerOnLine < self.center[1]:
                return self.arc < 180
            else:
                return self.arc > 180

class Node:
    __COUNTER = 0
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.edges = []
        self.id = Node.__COUNTER
        Node.__COUNTER += 1
    def addEdge(self,edge):
        self.edges.append(edge)

class Edge:
    __COUNTER = 0
    def __init__(self,distance,nodes):
        self.dist = distance
        self.nodes = nodes
        self.id = Edge.__COUNTER
        Edge.__COUNTER += 1
    def returnOtherNode(self,node):
        if self.nodes[0] == node:
            return self.nodes[1]
        else:
            return self.nodes[0]
    def getWeight(self):
        return abs(sqrt((self.nodes[1].x-self.nodes[0].x)**2 + (self.nodes[1].y-self.nodes[0].y)**2))
    def hasNode(self,id):
        for i in range(length(self.nodes)):
            if self.nodes[i].id == id:
                return True
        return False

class Pathfinder:
    def __init__(self,lines):
        self.segments = lines
        self.nodes = [] #   nodes  : List of all nodes, with the index being each ones id.
        self.edges = [] #   edges  : List of all edges, with the index being each ones id.
        self.dict = {} #    dict   : Dictionary with the id of each node as a Key, and each connected edge as a Value.
        self.path = [] #    path   : A list of the edges used in the optimal path. Each edge is indicated by its id.
        self.done = False # done   : Flag raised when pathfinding has been completed.
        self.gcode = "" #   gcode  : String holding complete gcode for given character.

    def pathfind(self):
        # SELECT STARTING POINT (arbitrarily)
        self.dict = self.initDictionary()
        costs = [0] * length(self.nodes)
        minCost = 1000000
        minPath = []
        for i in range(length(nodes)):
            vEdges = [0] * length(self.edges)
            ######
            dfs(vEdges,i,costs,i)
            ######
            if costs[i] < minCost:
                minCost = costs[i]
                minPath = path
        #
        path = minPath
        self.done = True

    # vEdges : List of boolean values indicating whether the corresponding edge has been visited. When all values are true, exit.
    # nodeID : Holds the current state of the recursive function, ie what node it is currently on.
    # costs  : Holds the cost of the path for each starting point. Indexed by startPt.
    # startPt: The node that was first in the path for this iteration. Used to index costs.
    def dfs(self,vEdges,nodeID,costs,startPt):
        if 0 not in vEdges:
            break


    # Converts edges in the optimized order into gcode
    def convert(self):
        self.gcode = ""
        curLine = ""
        lastPoint = (0,0)
        self.gcode += "G01 X0 Y0 Z0\n"
        for line in self.segments:
            curLine = ""
            if line.checkPickup(lastPoint):
                curLine += "G01 X" + str(line.start[0]) + " Y" + str(line.start[1]) + " Z0\n"
                lastPoint = line.end
            if line.center[0] == -1 and line.center[1] == -1:
                curLine += "G01 "
            else: # TODO: Logic determining CW / CCW
                if line.checkDirection():
                    curLine += "G02 "
                else:
                    curLine += "G03 "
            curLine += "X" + str(line.end[0]) + " Y" + str(line.end[1]) + " Z1"
            lastPoint = line.end
            if line.center[0] != -1 and line.center[1] != -1:
                curLine += " I" + str(line.getRelativeOf(line.center)[0]) + " J" + str(line.getRelativeOf(line.center)[1])
            self.gcode += curLine + "\n"

    # Variant of convert function that keeps the Z value set to 0 for debugging purposes.
    def convertConstZ(self):
        self.gcode = ""
        curLine = ""
        lastPoint = (0,0)
        self.gcode += "G01 X0 Y0 Z0\n"
        for line in self.segments:
            curLine = ""
            if line.checkPickup(lastPoint):
                curLine += "G01 X" + str(line.start[0]) + " Y" + str(line.start[1]) + " Z0\n"
                lastPoint = line.end
            if line.center[0] == -1 and line.center[1] == -1:
                curLine += "G01 "
            else: # TODO: Logic determining CW / CCW
                if line.checkDirection():
                    curLine += "G02 "
                else:
                    curLine += "G03 "
            curLine += "X" + str(line.end[0]) + " Y" + str(line.end[1]) + " Z0"
            lastPoint = line.end
            if line.center[0] != -1 and line.center[1] != -1:
                curLine += " I" + str(line.getRelativeOf(line.center)[0]) + " J" + str(line.getRelativeOf(line.center)[1])
            self.gcode += curLine + "\n"

    def getDistance(self,line,nA,nB):
        if line.center[0] == -1:
            return abs(sqrt((nB.x-nA.x)**2 + (nB.y-nA.y)**2))
        else: # NEEDS TO BE FIXED TO HANDLE OVALS
            radius = abs(sqrt((nA.x-line.center.x)**2 + (nA.y-line.center.y)**2))
            return line.arc * (math.pi / 180) * radius

    def nodify(self):
        print("Convert Lines to Nodes and Edges")
        for line in self.segments:
            self.nodes.append(Node(line.start[0],line.start[1]))
            self.nodes.append(Node(line.end[0],line.end[1]))
            self.edges.append(Edge(self.getDistance(line,self.nodes[-1],self.nodes[-2]),[self.nodes[-2],self.nodes[-1]))
            self.nodes[-2].addEdge(self.edges[-1])
            self.nodes[-1].addEdge(self.edges[-1])

    def initDictionary(self):
        dict = {}
        for i in range(length(self.nodes)):
            dict[i] = []
            for edge in self.edges:
                if edge.hasNode(i):
                    dict[i].append(edge)
        return dict

    def deNodify(self):
        print("Convert Nodes and Edges to Lines")

    def checkDone(self):
        return self.done

    def getGCode(self):
        return self.gcode
