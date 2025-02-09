import random
class Goal:
    def __init__(self,id,x=0,y=0,value=1):
        self.id = id
        self.x = x
        self.y = y
        self.value = value

    def set_random_goal(self, x_max, y_max):
        self.x = random.randint(0, x_max-1)
        self.y = random.randint(0, y_max-1)
        self.value = random.random()
