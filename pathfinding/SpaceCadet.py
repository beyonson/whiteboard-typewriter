class SpaceCadet:
    xMax = 4 # 60
    yMax = 3 # 40
    def __init__(self,size):
        self.size = size
        self.x = 0
        self.y = SpaceCadet.yMax - size
    def plot(self,coord):
        x = (coord[0] * self.size) + self.x
        #x = coord[0] #+ self.x
        y = (coord[1] * self.size) + self.y
        #y = coord[1] #+ self.y
        return (x,y)
    def step(self):
        self.x += self.size
        if self.x + self.size > SpaceCadet.xMax:
            self.x = 0
            self.y -= self.size
