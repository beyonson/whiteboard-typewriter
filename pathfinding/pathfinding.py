# g-code Commands
#
# G01 X# Y# Z# F#: Draws a straight line to (X, Y) at F speed. Z=0 means marker is up. Z=1 means marker is down.
# G02 X# Y# Z# I# J# F#: Draws a curved line to (X, Y) at F speed, rotating clockwise about (I, J). Z=0 means marker is up. Z=1 means marker is down.
# G03 X# Y# Z# I# J# F#: Draws a curved line to (X, Y) at F speed, rotating counter-clockwise about (I, J). Z=0 means marker is up. Z=1 means marker is down.
# G17: Write on XY plane
# G20: Set units to inches
# G21: Set units to millimeters
# G28: Return home

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

class Pathfinder:
    def __init__(self,lines):
        self.segments = lines
        self.done = False
        self.gcode = ""
    def translate(self):
        print("TRANSLATE")
        # BLANK: May not be necessary
    def pathfind(self):
        self.done = True
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
    def checkDone(self):
        return self.done
    def getGCode(self):
        return self.gcode
