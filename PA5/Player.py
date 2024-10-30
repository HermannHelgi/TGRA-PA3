class Player:

    def __init__(self,
                 position:list=[0,0,0],
                 rotation:list=[0,0,0],
                 points = 0,
                 ):
        self.position = position
        self.rotation = rotation
        self.points = points

    def update(self):
        pass

    def draw(self):
        pass
