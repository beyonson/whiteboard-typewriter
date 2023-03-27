from pathfinding import *
import time

cadet = SpaceCadet(1)

# STRAIGHT LINE TEST: Draw a box
lines = []
lines.append(Line(.199,.2,.2,.4))
lines.append(Line(.4,.2,.2,.2))
lines.append(Line(.2,.4,.4,.4001))
lines.append(Line(.4,.4,.4,.2))

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
pathfinder.pathfind()
if pathfinder.checkDone():
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing box:")
print(gcode)
cadet.step()

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
lines.append(Line(.7,.6,.6,.5,.6,.6,90)) # 3
lines.append(Line(.5,.6,.6,.7,.6,.6,90)) # 1
lines.append(Line(.6,.7,.7,.6,.6,.6,90)) # 2
lines.append(Line(.6,.5,.5,.6,.6,.6,90)) # 4
lines.append(Line(.9,.8,.8,.7,.8,.8,90)) # 3
lines.append(Line(.7,.8,.8,.9,.8,.8,90)) # 1
lines.append(Line(.8,.9,.9,.8,.8,.8,90)) # 2
lines.append(Line(.8,.7,.7,.8,.8,.8,90)) # 4

pathfinder = Pathfinder(lines)
pathfinder.setVerbosity(False)
gcode = ""
start = time.time()
pathfinder.pathfind()
end = time.time()
print(f'Circle test took {end-start}s')
if pathfinder.checkDone():
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing circle (CW):")
print(gcode)
cadet.step()

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
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing semicircle (CCW):")
print(gcode)
cadet.step()

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
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing two arcs (CW/CCW):")
print(gcode)
cadet.step()

################################################################
# CURVED LINE TEST: Draw a Circle and Square (CW)

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
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing a Circle and Square:")
print(gcode)
cadet.step()

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
    pathfinder.convert(cadet)
    gcode = pathfinder.getGCode()

print("Drawing the letter L:")
print(gcode)
cadet.step()
