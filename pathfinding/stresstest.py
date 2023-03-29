from pathfinding import *
import time

def lineGen(intensity):
    lines = []
    for i in range(intensity):
        x = i/intensity
        lines.append(Line(0+x,0,0+x,1))
        lines.append(Line(0+x,1,((i+1)/intensity),0,0+x,.5))
    lines.append(Line(2,0,2,1))
    print(len(lines))
    return lines

for intensity in range(1,12):
    cadet = SpaceCadet(1)
    pathfinder = Pathfinder(lineGen(intensity))
    pathfinder.setVerbosity(False)
    gcode = ""
    start = time.time()
    pathfinder.pathfind()
    if pathfinder.checkDone():
        pathfinder.convert(cadet)
        end = time.time()
        print(f'With intensity {intensity} took {end-start}')
        gcode = pathfinder.getGCode()
    print(gcode)
    cadet.step()
