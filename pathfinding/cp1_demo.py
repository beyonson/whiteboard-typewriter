from pathfinding import *

# STRAIGHT LINE TEST: Draw a box
lines = []
lines.append(Line(.2,.2,.2,.4))
lines.append(Line(.2,.4,.4,.4))
lines.append(Line(.4,.4,.4,.2))
lines.append(Line(.4,.2,.2,.2))

pathfinder = Pathfinder(lines)
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
lines.append(Line(.1,.2,.2,.3,.2,.2,90))
lines.append(Line(.2,.3,.3,.2,.2,.2,90))
lines.append(Line(.3,.2,.2,.1,.2,.2,90))
lines.append(Line(.2,.1,.1,.2,.2,.2,90))

pathfinder = Pathfinder(lines)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing circle (CW):")
print(gcode)

################################################################
# CURVED LINE TEST: Draw a circle (CCW)

lines = []
lines.append(Line(.1,.2,.2,.1,.2,.2,90))
lines.append(Line(.2,.1,.3,.2,.2,.2,90))
lines.append(Line(.3,.2,.2,.3,.2,.2,90))
lines.append(Line(.2,.3,.1,.2,.2,.2,90))

pathfinder = Pathfinder(lines)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing circle (CCW):")
print(gcode)

################################################################
# CURVED LINE PICKUP TEST: Draw two arcs

lines = []
lines.append(Line(.1,.3,.2,.4,.2,.3,90))
lines.append(Line(.2,.4,.3,.3,.2,.3,90))
lines.append(Line(.3,.2,.2,.3,.2,.2,90))
lines.append(Line(.2,.3,.1,.2,.2,.2,90))

pathfinder = Pathfinder(lines)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert()
    gcode = pathfinder.getGCode()

print("Drawing two arcs (CCW):")
print(gcode)
