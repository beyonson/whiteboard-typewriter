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
from SpaceCadet import *

def clean():
    Edge.resetCounter()
    Node.resetCounter()

class PathfindingPackage:
    def __init__(self,lines,letter,font):
        self.lines = lines
        self.letter = letter
        self.font = font

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
    def flip(self):
        temp = self.start
        self.start = self.end
        self.end = temp
    def checkDirection(self): # T = CW, F = CCW
        # Check if C is above or below line
        if self.end[0] - self.start[0] != 0:
            slope = (self.end[1] - self.start[1]) / (self.end[0] - self.start[0])
        else:
            slope = 1000000
        yint = self.start[1] - (slope * self.start[0])
        centerOnLine = (self.center[0] * slope) + yint
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
    @classmethod
    def resetCounter(cls):
        cls.__COUNTER = 0

class Edge:
    __COUNTER = 0
    def __init__(self,distance,nodes):
        self.dist = distance
        self.nodes = nodes
        self.id = Edge.__COUNTER
        Edge.__COUNTER += 1
    def otherNode(self,node):
        if self.nodes[0].id == node.id:
            return self.nodes[1]
        else:
            return self.nodes[0]
    def getWeight(self):
        return self.dist
    def hasNode(self,id):
        for i in range(len(self.nodes)):
            if self.nodes[i].id == id:
                return True
        return False
    def getID(self):
        return self.id
    @classmethod
    def resetCounter(cls):
        cls.__COUNTER = 0

class Pathfinder:
    def __init__(self,lines):
        clean()
        self.segments = lines
        self.verbose = False
        self.nodes = [] #     nodes          : List of all nodes, with the index being each ones id.
        self.edges = [] #     edges          : List of all edges, with the index being each ones id.
        self.dict = {} #      dict           : Dictionary with the id of each node as a Key, and each connected edge as a Value.
        self.path = [] #      path           : A list of the edges used and jumps in the working path. Each edge is indicated by its id, and jumps by either -1 or destination node.
        self.minPath = [] #   minPath        : A list of the edges used and jumps in the optimal path. Each edge is indicated by its id, and jumps by either -1 or destination node
        self.costs = [] #     costs          : A list of the relative costs for each edge in a character for a given starting node. Each edge is indicated by its id.
        self.startPt = 0 #    startPt        : Integer to keep track of what node was chosen as the starting point.
        self.done = False #   done           : Flag raised when pathfinding has been completed.
        self.gcode = "" #     gcode          : String holding complete gcode for given character.
        self.standardize()
        self.snap()

    def pathfind(self):
        self.nodify()
        self.dict = self.initDictionary() # Initialize dictionary data structure for pathfinding
        self.costs = [1000000] * len(self.nodes) # Initialize costs vector
        self.minCost = 1000000 # Initializing minimum cost to be a huge number
        finalPath = []
        startPoints = self.findStart()
        if len(startPoints) == 0:
            startPoints = self.nodes
        for i in range(len(startPoints)): # Iterate through possible starting nodes
            self.xPrint(f'Iterating over {startPoints[i].id}')
            self.startPt = startPoints[i].id
            temp = ""
            vEdges = [0] * len(self.edges)
            self.path = []
            self.minPath = []
            self.dfs(vEdges[:],startPoints[i].id,0) # Enter DFS function at starting node (Initial cost = 0, jump = -1)
            self.xPrint(f'Cost of DFS at {startPoints[i].id}: {self.costs[self.startPt]}. Path was {self.minPath}')
            if self.costs[self.startPt] < self.minCost: # Check if most recent iteration had the optimal cost
                self.minCost = self.costs[i] # Set minimum cost to most recent cost
                finalPath = self.minPath.copy() # Set optimal path to that of the most recent iteration
            ideal = True
            for step in finalPath:
                if step[1] != -1:
                    ideal = False
            if ideal:
                break
        self.minPath = finalPath
        self.xPrint(f'Pathfinding complete! Final path is: {self.minPath}')
        self.deNodify()
        self.done = True # Raise done flag

    # vEdges   : String of boolean values indicating whether the corresponding edge has been visited. When all values are true, exit.
    # nodeID   : Holds the current state of the recursive function, ie what node it is currently on.
    # cost     : Holds the cost of the working path.
    def dfs(self,vEdges,nodeID,cost):
        if len(self.path) > 0: # If this is not the first node
            if self.path[-1][1] == -1: # If the node has not been reached as the result of a jump
                cost += self.edges[self.path[-1][0]].getWeight() # Calculate weight of the edge that was just traversed
                vEdges[self.path[-1][0]] = 1 # Mark edge as visited
            else: # If the node has been reached as the result of a jump
                cost += self.edges[self.path[-1][0]].getWeight() # Calculate weight of the edge that was just traversed
                cost += abs(math.sqrt((self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).x-self.nodes[self.path[-1][1]].x)**2 + (self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).y-self.nodes[self.path[-1][1]].y)**2)) # Calculate and add the cost of the jump
                vEdges[self.path[-1][0]] = 1 # Mark edge as visited
        #self.xPrint(f'DFS: Path: {self.path}, CurrentNode: {nodeID}, Cost: {cost}, vEdges: {vEdges}')
        if 0 not in vEdges: # If all edges have been visited
            if cost < self.costs[self.startPt]: # If cost is less than last min
                self.costs[self.startPt] = cost # Set cost as new min
                self.minPath = self.path.copy() # Set current path as minPath
            self.path.pop(-1) # Remove last entry from path
            return True # Return to last recursion
        validPath = 0 # Preset flag to 0)
        for i in range(len(self.dict[nodeID])): # Check unvisited edges
            if vEdges[self.dict[nodeID][i].id] == 0: # If edge i is unvisited
                self.path.append(tuple((self.dict[nodeID][i].id,-1))) # Add i to path
                self.dfs(vEdges[:],self.dict[nodeID][i].otherNode(self.nodes[nodeID]).id,cost) # Recurse on node opposite of nodeID over edge i
                validPath = 1 # Mark that a valid path was found
        if validPath == 0: # If all edges around nodeID were already visited
            for i in range(len(self.edges)): # Search over all edges
                if vEdges[i] == 0: # If edge i has not been visited
                    self.path.append(tuple((self.edges[i].id,nodeID))) # Add unvisited edge to path
                    self.dfs(vEdges[:],self.edges[i].nodes[0].id,cost) # Jump to and recurse over 1st node of unvisited edge
                    self.path.append(tuple((self.edges[i].id,nodeID))) # Add unvisited edge to path
                    self.dfs(vEdges[:],self.edges[i].nodes[1].id,cost) # Jump to and recurse over 2nd node of unvisited edge
        if len(self.path) > 0: # If this is not the first node
            self.path.pop(-1) # Remove last entry from path
        return False # Return to last recursion

    def snap(self,sensitivity=.005):
        for i in range(len(self.segments)):
            for j in range(i+1,len(self.segments)):
                dist = self.getPointDistance(self.segments[i].start,self.segments[j].start)
                if dist < sensitivity and dist != 0:
                    self.segments[i].start = self.segments[j].start
                    continue
                dist = self.getPointDistance(self.segments[i].start,self.segments[j].end)
                if dist < sensitivity and dist != 0:
                    self.segments[i].start = self.segments[j].end
                    continue
                dist = self.getPointDistance(self.segments[i].end,self.segments[j].start)
                if dist < sensitivity and dist != 0:
                    self.segments[i].end = self.segments[j].start
                    continue
                dist = self.getPointDistance(self.segments[i].end,self.segments[j].end)
                if dist < sensitivity and dist != 0:
                    self.segments[i].end = self.segments[j].end
                    continue

    def standardize(self):
        max = 0
        min = 1000000
        for line in self.segments:
            if line.start[0] > max:
                max = line.start[0]
            if line.start[1] > max:
                max = line.start[1]
            if line.end[0] > max:
                max = line.end[0]
            if line.end[1] > max:
                max = line.end[1]
            if line.start[0] < min:
                min = line.start[0]
            if line.start[1] < min:
                min = line.start[1]
            if line.end[0] < min:
                min = line.end[0]
            if line.end[1] < min:
                min = line.end[1]
        if max < 1:
            return
        max += max * .1
        for line in self.segments:
            editLineS = list(line.start)
            editLineE = list(line.end)
            editLineC = list(line.center)
            editLineS[0] -= min
            editLineS[0] /= max
            editLineS[1] -= min
            editLineS[1] /= max
            editLineE[0] -= min
            editLineE[0] /= max
            editLineE[1] -= min
            editLineE[1] /= max
            if editLineC[0] != -1 or editLineC[1] != -1:
                editLineC[0] -= min
                editLineC[0] /= max
                editLineC[1] -= min
                editLineC[1] /= max
            line.start = tuple(editLineS)
            line.end = tuple(editLineE)
            line.center = tuple(editLineC)

    # Converts edges in the optimized order into gcode
    def convert(self,spacer):
        self.gcode = ""
        curLine = ""
        lastPoint = (0,0)
        start = spacer.plot(lastPoint)
        self.gcode += "G01 X" + str(start[0]) + " Y" + str(start[1]) + " Z0\n"
        for line in self.segments:
            curLine = ""
            if line.checkPickup(lastPoint):
                curLine += "G01 X" + str(spacer.plot(line.start)[0]) + " Y" + str(spacer.plot(line.start)[1]) + " Z0\n"
                lastPoint = line.end
            if line.center[0] == -1 and line.center[1] == -1:
                curLine += "G01 "
            else:
                if line.checkDirection():
                    curLine += "G02 "
                else:
                    curLine += "G03 "
            curLine += "X" + str(spacer.plot(line.end)[0]) + " Y" + str(spacer.plot(line.end)[1]) + " Z1"
            lastPoint = line.end
            if line.center[0] != -1 and line.center[1] != -1:
                curLine += " I" + str(line.getRelativeOf(line.center)[0]) + " J" + str(line.getRelativeOf(line.center)[1])
            self.gcode += curLine + "\n"

    # Variant of convert function that keeps the Z value set to 0 for debugging purposes.
    def convertConstZ(self,spacer):
        self.gcode = ""
        curLine = ""
        lastPoint = (0,0)
        start = spacer.plot(lastPoint)
        self.gcode += "G01 X" + str(start[0]) + " Y" + str(start[1]) + " Z0\n"
        for line in self.segments:
            curLine = ""
            if line.checkPickup(lastPoint):
                curLine += "G01 X" + str(spacer.plot(line.start)[0]) + " Y" + str(spacer.plot(line.start)[1]) + " Z0\n"
                lastPoint = line.end
            if line.center[0] == -1 and line.center[1] == -1:
                curLine += "G01 "
            else:
                if line.checkDirection():
                    curLine += "G02 "
                else:
                    curLine += "G03 "
            curLine += "X" + str(spacer.plot(line.end)[0]) + " Y" + str(spacer.plot(line.end)[1]) + " Z0"
            lastPoint = line.end
            if line.center[0] != -1 and line.center[1] != -1:
                curLine += " I" + str(line.getRelativeOf(line.center)[0]) + " J" + str(line.getRelativeOf(line.center)[1])
            self.gcode += curLine + "\n"

    def getDistance(self,line,nA,nB):
        if line.center[0] == -1:
            return abs(math.sqrt((nB.x-nA.x)**2 + (nB.y-nA.y)**2))
        else:
            radius = abs(math.sqrt((nA.x-line.center[0])**2 + (nA.y-line.center[1])**2))
            return line.arc * (math.pi / 180) * radius

    def getPointDistance(self,a,b):
        return abs(math.sqrt((b[1]-a[1])**2 + (b[0]-a[0])**2))

    def nodify(self):
        self.xPrint("Convert Lines to Nodes and Edges") # FIX : Include possibility of shared points
        for line in self.segments:
            nodeA = -10
            nodeB = -10
            for i in range(len(self.nodes)):
                if self.nodes[i].x == line.start[0] and self.nodes[i].y == line.start[1]:
                    nodeA = i
                if self.nodes[i].x == line.end[0] and self.nodes[i].y == line.end[1]:
                    nodeB = i
            if nodeA == -10:
                self.nodes.append(Node(line.start[0],line.start[1]))
                nodeA = len(self.nodes) - 1
            if nodeB == -10:
                self.nodes.append(Node(line.end[0],line.end[1]))
                nodeB = len(self.nodes) - 1
            self.edges.append(Edge(self.getDistance(line,self.nodes[nodeA],self.nodes[nodeB]),[self.nodes[nodeA],self.nodes[nodeB]]))
            self.nodes[nodeA].addEdge(self.edges[-1])
            self.nodes[nodeB].addEdge(self.edges[-1])
        self.xPrint(f'Nodification complete! Nodes: {len(self.nodes)}, Edges: {len(self.edges)}')

    def initDictionary(self):
        dict = {}
        for i in range(len(self.nodes)):
            dict[i] = []
            for edge in self.edges:
                if edge.hasNode(i):
                    dict[i].append(edge)
        self.xPrint(f'Dictionary initialized! Contains:')
        for i in range(len(dict)):
            self.xPrint(f'{i} - ')
            for j in range(len(dict[i])):
                self.xPrint(f' {dict[i][j].id}')
        return dict

    def findStart(self):
        instances = {}
        startPoints = []
        for edge in self.edges:
            for node in edge.nodes:
                if node.id in instances:
                    instances[node.id] += 1
                else:
                    instances[node.id] = 1
        for i in range(len(instances)):
            if instances[i] < 2:
                startPoints.append(self.nodes[i])
        self.xPrint(instances)
        return startPoints

    def deNodify(self):
        self.xPrint("Convert Nodes and Edges to Lines")
        newLines = [-1] * len(self.segments)
        for i in range(len(newLines)):
            newLines[i] = self.segments[self.minPath[i][0]]
        if newLines[0].start == newLines[1].start or newLines[0].start == newLines[1].end:
            newLines[0].flip()
        for i in range(len(newLines)-1):
            if newLines[i].end != newLines[i+1].start:
                if self.minPath[i+1][1] == -1:
                    newLines[i+1].flip()
                elif newLines[i+1].start[0] != self.nodes[self.minPath[i+1][1]].x or newLines[i+1].start[1] != self.nodes[self.minPath[i+1][1]].y:
                    newLines[i+1].flip()
        self.segments = newLines

    def checkDone(self):
        return self.done

    def getGCode(self):
        return self.gcode

    def setVerbosity(self,v):
        self.verbose = v

    def xPrint(self,output):
        if self.verbose == True:
            print(output)
