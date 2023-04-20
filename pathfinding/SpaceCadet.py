class SpaceCadet:
    xMax = 8 # 60
    yMax = 5.5 # 40
    def __init__(self,size):
        self.size = size
        self.x = 0
        self.y = 0
        self.slowdown = False
    def plot(self,coord):
        x = (coord[0] * self.size) + self.x
        #x = coord[0] #+ self.x
        y = (coord[1] * self.size) + self.y
        #y = coord[1] #+ self.y
        return (x,y)
    def step(self):
        self.x += (self.size*.6)
        if self.x + (self.size*.6) > SpaceCadet.xMax:
            self.nextLine()
        else:
            self.slowdown = False
    def reset(self):
        self.x = 0
        self.y = 0
    def nextLine(self):
        self.slowdown = True
        self.x = 0
        self.y += self.size
        if self.y > SpaceCadet.yMax:
            self.y = 0
    def newSize(self,size):
        actualSize = 1.5 + ((size-12)*.25)
        self.size = actualSize
        print(f'Set size to {size}')