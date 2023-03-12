from pathfinding import *

# STRAIGHT LINE TEST: Draw a box
lines = []
lines.append(Line(.2,.2,.2,.4))
lines.append(Line(.4,.2,.2,.2))
lines.append(Line(.2,.4,.4,.4))
lines.append(Line(.4,.4,.4,.2))

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing box:")
print(gcode)

################################################################
# CURVED LINE TEST: Draw a circle (CW)

lines = []
lines.append(Line(.3,.2,.2,.1,.2,.2,90)) # 3
lines.append(Line(.1,.2,.2,.3,.2,.2,90)) # 1
lines.append(Line(.2,.3,.3,.2,.2,.2,90)) # 2
lines.append(Line(.2,.1,.1,.2,.2,.2,90)) # 4
lines.append(Line(.5,.4,.4,.3,.4,.4,90)) # 3
lines.append(Line(.3,.4,.4,.5,.4,.4,90)) # 1
lines.append(Line(.4,.5,.5,.4,.4,.4,90)) # 2
lines.append(Line(.4,.3,.3,.4,.4,.4,90)) # 4

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing circle (CW):")
print(gcode)

################################################################
# CURVED LINE TEST: Draw a semicircle (CCW)

lines = []
lines.append(Line(.1,.2,.2,.1,.2,.2,90))
lines.append(Line(.2,.1,.3,.2,.2,.2,90))
lines.append(Line(.3,.2,.1,.2))
#lines.append(Line(.2,.3,.1,.2,.2,.2,90))

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing semicircle (CCW):")
print(gcode)

################################################################
# CURVED LINE PICKUP TEST: Draw two arcs

lines = []
lines.append(Line(.1,.3,.2,.4,.2,.3,90))
lines.append(Line(.2,.4,.3,.3,.2,.3,90))
lines.append(Line(.3,.2,.2,.3,.2,.2,90))
lines.append(Line(.2,.3,.1,.2,.2,.2,90))

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing two arcs (CW/CCW):")
print(gcode)

################################################################
# CURVED LINE TEST: Draw a circle (CW)

lines = []
lines.append(Line(.2,.2,.2,.4))
lines.append(Line(.4,.2,.2,.2))
lines.append(Line(.2,.4,.4,.4))
lines.append(Line(.4,.4,.4,.2))
lines.append(Line(.5,.4,.4,.3,.4,.4,90)) # 3
lines.append(Line(.3,.4,.4,.5,.4,.4,90)) # 1
lines.append(Line(.4,.5,.5,.4,.4,.4,90)) # 2
lines.append(Line(.4,.3,.3,.4,.4,.4,90)) # 4

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing a circle and square:")
print(gcode)

###############################################################
# SIMPLE LETTER TEST: Drawing L

lines = []
lines.append(Line(628.234,1427.96,929,1427.96))
lines.append(Line(563.456,1376.21,563.456,876.21))
lines.append(Line(563.456,1376.21,628.234,1427.96,626,1364,51.75))

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing the letter L:")
print(gcode)
