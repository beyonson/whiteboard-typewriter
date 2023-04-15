class SpaceCadet:
    xMax = 15 # 60
    yMax = 10 # 40
    def __init__(self,size):
        self.size = size
        self.x = 0
        self.y = 0
    def plot(self,coord):
        x = (coord[0] * self.size) + self.x
        #x = coord[0] #+ self.x
        y = (coord[1] * self.size) + self.y
        #y = coord[1] #+ self.y
        return (x,y)
    def step(self):
        self.x += (self.size*.6)
        if self.x + (self.size*.6) > SpaceCadet.xMax:
            self.x = 0
            self.y += self.size
            if self.y > SpaceCadet.yMax:
                self.y = SpaceCadet.yMax
    def reset(self):
        self.x = 0
        self.y = 0
    def nextLine(self):
        self.x = 0
        self.y += self.size
        if self.y > SpaceCadet.yMax:
            self.y = SpaceCadet.yMax
