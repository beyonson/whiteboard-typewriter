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
import time

def clean():
    Edge.resetCounter()
    Node.resetCounter()

class PathfindingPackage:
    def __init__(self,lines,letter,font,type="None"):
        self.lines = lines
        self.letter = letter
        self.font = font
        self.type = type

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
    def coords(self):
        return tuple((self.x,self.y))
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
    def __init__(self,lines,sensitivity=.025):
        clean()
        self.segments = lines
        self.verbose = False
        self.nodes = [] #      nodes          : List of all nodes, with the index being each ones id.
        self.edges = [] #      edges          : List of all edges, with the index being each ones id.
        self.dict = {} #       dict           : Dictionary with the id of each node as a Key, and each connected edge as a Value.
        self.path = [] #       path           : A list of the edges used and jumps in the working path. Each edge is indicated by its id, and jumps by either -1 or destination node.
        self.minPath = [] #    minPath        : A list of the edges used and jumps in the optimal path. Each edge is indicated by its id, and jumps by either -1 or destination node
        self.costs = [] #      costs          : A list of the relative costs for each edge in a character for a given starting node. Each edge is indicated by its id.
        self.startPt = 0 #     startPt        : Integer to keep track of what node was chosen as the starting point.
        self.done = False #    done           : Flag raised when pathfinding has been completed.
        self.gcode = "" #      gcode          : String holding complete gcode for given character.
        self.ripcord = -1 #    ripcord        : Float holding the amount of time that is allowed to be spent on pathfinding before exiting, if set.
        self.currentCode = -1 #currentCode    : Integer holding the current gcode command in place
        self.speed = 300 #   speed          : Integer holding the feed rate printed in gcode
        self.standardize()
        self.snap(sensitivity)

    def pathfind(self):
        start = time.time()
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
            if ideal or (self.ripcord >= 0 and time.time() - start > self.ripcord):
                if self.ripcord >= 0 and time.time() - start > self.ripcord:
                    self.xPrint("Rip!")
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
            if self.path[-1][1] != -1:
                cost += abs(math.sqrt((self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).x-self.nodes[self.path[-1][1]].x)**2 + (self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).y-self.nodes[self.path[-1][1]].y)**2)) # Calculate and add the cost of the jump
                self.path[-1] = tuple((self.path[-1][0],self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).id)) # Replace jump value with jump destination for easier gcode generation | self.edges[self.path[-1][0]].otherNode(self.nodes[nodeID]).id
            cost += self.edges[self.path[-1][0]].getWeight() # Calculate weight of the edge that was just traversed
            vEdges[self.path[-1][0]] = 1 # Mark edge as visited
        #self.xPrint(f'DFS: Path: {self.path}, CurrentNode: {nodeID}, Cost: {cost}, vEdges: {vEdges}')
        if 0 not in vEdges: # If all edges have been visited
            if cost < self.costs[self.startPt]: # If cost is less than last min
                self.costs[self.startPt] = cost # Set cost as new min
                self.minPath = self.path.copy() # Set current path as minPath
            self.path.pop(-1) # Remove last entry from path
            return True # Return to last recursion
        validPath = 0 # Preset flag to 0
        for i in range(len(self.dict[nodeID])): # Check unvisited edges
            if vEdges[self.dict[nodeID][i].id] == 0: # If edge i is unvisited
                self.path.append(tuple((self.dict[nodeID][i].id,-1))) # Add i to path
                self.dfs(vEdges[:],self.dict[nodeID][i].otherNode(self.nodes[nodeID]).id,cost) # Recurse on node opposite of nodeID over edge i
                validPath = 1 # Mark that a valid path was found
        if validPath == 0: # If all edges around nodeID were already visited
            idealNodes = []
            priorGood = False # Flag marking whether an optimal jump point is found
            for i in range(len(self.nodes)): # Search over all nodes
                possEdges = 0 # Counter to count each unvisited edge attached to node i
                for j in range(len(self.dict[i])): # Search over all edges attached to node i
                    if vEdges[self.dict[i][j].id] == 0: # If this edge has not been visited
                        possEdges += 1 # Increment counter
                if possEdges == 1: # If there is only one unvisited edge from node i
                    priorGood = True # Mark that an optimal jump point has been found
                    idealNodes.append(i)
            if len(idealNodes) <= 3:
                for i in range(len(idealNodes)):
                    for j in range(len(self.dict[idealNodes[i]])): # Search through all attached edges to node i
                        if vEdges[self.dict[idealNodes[i]][j].id] == 0: # If edge is unvisited
                            #print(f'Jump to {i}')
                            if self.edges[self.dict[idealNodes[i]][j].id].nodes[0].id != i:
                                self.path.append(tuple((self.edges[self.dict[idealNodes[i]][j].id].id,nodeID))) # Add unvisited edge to path
                                if self.dfs(vEdges[:],self.edges[self.dict[idealNodes[i]][j].id].nodes[0].id,cost): # Jump to and recurse over target node of unvisited edge
                                    break
                            else:
                                self.path.append(tuple((self.edges[self.dict[idealNodes[i]][j].id].id,nodeID))) # Add unvisited edge to path
                                if self.dfs(vEdges[:],self.edges[self.dict[idealNodes[i]][j].id].nodes[1].id,cost): # Jump to and recurse over target node of unvisited edge
                                    break
            else:
                ideals = self.shortestJump(nodeID,idealNodes,1)
                for i in range(len(ideals)):
                    for j in range(len(self.dict[ideals[i]])): # Search through all attached edges to node i
                        if vEdges[self.dict[ideals[i]][j].id] == 0: # If edge is unvisited
                            #print(f'Jump to {i}')
                            if self.edges[self.dict[ideals[i]][j].id].nodes[0].id != i:
                                self.path.append(tuple((self.edges[self.dict[ideals[i]][j].id].id,nodeID))) # Add unvisited edge to path
                                if self.dfs(vEdges[:],self.edges[self.dict[ideals[i]][j].id].nodes[0].id,cost): # Jump to and recurse over target node of unvisited edge
                                    break
                            else:
                                self.path.append(tuple((self.edges[self.dict[ideals[i]][j].id].id,nodeID))) # Add unvisited edge to path
                                if self.dfs(vEdges[:],self.edges[self.dict[ideals[i]][j].id].nodes[1].id,cost): # Jump to and recurse over target node of unvisited edge
                                    break
            if not priorGood: # If no optimal jump point is found
                for i in range(len(self.edges)): # Search over all edges
                    if vEdges[i] == 0: # If edge i has not been visited
                        #print(f'NonPriority Jump to {self.edges[i].nodes[0].id}')
                        self.path.append(tuple((self.edges[i].id,nodeID))) # Add unvisited edge to path
                        self.dfs(vEdges[:],self.edges[i].nodes[0].id,cost) # Jump to and recurse over 1st node of unvisited edge
                        #print(f'NonPriority Jump to {self.edges[i].nodes[1].id}')
                        self.path.append(tuple((self.edges[i].id,nodeID))) # Add unvisited edge to path
                        self.dfs(vEdges[:],self.edges[i].nodes[1].id,cost) # Jump to and recurse over 2nd node of unvisited edge
        if len(self.path) > 0: # If this is not the first node
            self.path.pop(-1) # Remove last entry from path
        return False # Return to last recursion

    def shortestJump(self,source,dests,amt):
        candidate = 100
        minDists = [100] * amt
        ideals = [-1] * amt
        for i in range(len(dests)):
            dist = abs(math.sqrt((self.nodes[dests[i]].x-self.nodes[source].x)**2 + (self.nodes[dests[i]].y-self.nodes[source].y)**2))
            #print(f'{dests[i]}: {dist}')
            if dist < candidate:
                replacedFlag = False
                distMax = 0
                for j in range(len(minDists)):
                    if minDists[j] == candidate:
                        minDists[j] = dist
                        ideals[j] = dests[i]
                        replacedFlag = True
                    if minDists[j] > distMax:
                        distMax = minDists[j]
                candidate = distMax
        #print(f'--BEST-- {ideal}: {minDist}')
        while(ideals[-1]==100):
            ideals.pop()
        return ideals

    def setRipcord(self,rip=5):
        self.ripcord = rip

    def setSpeed(self,speed):
        self.speed = speed

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
    def convert(self,spacer,lines=""):
        self.currentCode = 0
        self.gcode = ""
        if lines == "":
            lines = self.segments
        curLine = ""
        lastPoint = (0,0)
        start = spacer.plot(lastPoint)
        self.gcode += "G01 X-" + str(round(spacer.plot(lastPoint)[0],4)) + " Y-" + str(round(spacer.plot(lastPoint)[1],4)) + " Z0 "
        if spacer.slowdown:
            self.gcode += "F100\n"
            spacer.slowdown = False
        else:
            self.gcode += "F" + str(self.speed/2.5) + "\n"
        for line in lines:
            curLine = ""
            if line.checkPickup(lastPoint):
                if lastPoint != (0,0):
                    curLine += "G01 Z0 F" + str(self.speed) + "\n"
                curLine += "G01 X-" + str(round(spacer.plot(line.start)[0],4)) + " Y-" + str(round(spacer.plot(line.start)[1],4)) + " Z0 F" + str(self.speed) + "\n"
                curLine += "G01 Z1.2 F" + str(self.speed) + "\n"
                lastPoint = line.end
            if line.center[0] == -1 and line.center[1] == -1:
                curLine += "G01 "
            else:
                if line.checkDirection():
                    curLine += "G02 "
                else:
                    curLine += "G03 "
            curLine += "X-" + str(round(spacer.plot(line.end)[0],4)) + " Y-" + str(round(spacer.plot(line.end)[1],4)) + " Z1.2"
            lastPoint = line.end
            if line.center[0] != -1 and line.center[1] != -1:
                curLine += " I-" + str(round(line.getRelativeOf(line.center)[0],4)) + " J-" + str(round(line.getRelativeOf(line.center)[1],4))
            self.gcode += curLine + " F" + str(self.speed) + "\n"
        self.gcode += "G01 X-" + str(round(spacer.plot(line.end)[0],4)) + " Y-" + str(round(spacer.plot(line.end)[1],4)) + " Z0 F" + str(self.speed) + "\n"

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
        return dict

    def findStart(self,threshold=.2):
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
        betterPts = []
        for pt in startPoints:
            #print(f'{self.nearestNode(pt)} > {threshold}')
            if self.nearestNode(pt) > threshold:
                betterPts.append(pt)
        print(f'betterPts: {len(betterPts)}, startPoints: {len(startPoints)}')
        if len(betterPts) > 0:
            return betterPts
        return startPoints

    def nearestNode(self,node):
        closest = 100
        nodeID = node.id
        for i in range(len(self.nodes)):
            if i == nodeID:
                continue
            dist = self.getPointDistance(self.nodes[nodeID].coords(),self.nodes[i].coords())
            #print(dist)
            if dist < closest:
                closest = dist
        return closest

    def deNodify(self):
        self.xPrint("Convert Nodes and Edges to Lines")
        orderedLines = [-1] * len(self.segments)
        jump = False
        for i in range(len(orderedLines)):
            orderedLines[i] = self.segments[self.minPath[i][0]]
        if orderedLines[0].start == orderedLines[1].start or orderedLines[0].start == orderedLines[1].end:
            orderedLines[0].flip()
        for i in range(len(orderedLines)-1):
            self.xPrint(f'{self.edges[self.minPath[i][0]].nodes[0].id} - {self.minPath[i][0]} - {self.edges[self.minPath[i][0]].nodes[1].id} (FROM {self.minPath[i][1]}), {self.edges[self.minPath[i+1][0]].nodes[0].id} - {self.minPath[i+1][0]} - {self.edges[self.minPath[i+1][0]].nodes[1].id} (FROM {self.minPath[i+1][1]})')
            #self.xPrint(f'orderedLines[i+1].end: {orderedLines[i+1].end} , self.nodes[self.minPath[i+1][1]].coords(): {self.nodes[self.minPath[i+1][1]].coords()}')
            if self.minPath[i+1][1] == -1 and orderedLines[i].end != orderedLines[i+1].start:
                self.xPrint("Flip A")
                orderedLines[i+1].flip()
            elif self.minPath[i+1][1] != -1 and orderedLines[i+1].end == self.nodes[self.minPath[i+1][1]].coords(): #  and orderedLines[i].end == orderedLines[i+1].end
                self.xPrint("Flip B")
                orderedLines[i+1].flip()
        for i in range(len(orderedLines)-1):
            if self.minPath[i+1][1] != -1 and self.getPointDistance(orderedLines[i].end,orderedLines[i+1].end) < self.getPointDistance(orderedLines[i].end,orderedLines[i+1].start):
                orderedLines[i+1].flip()
        self.segments = orderedLines

    def checkDone(self):
        return self.done

    def getGCode(self):
        return self.gcode

    def setVerbosity(self,v):
        self.verbose = v

    def xPrint(self,output):
        if self.verbose == True:
            print(output)
