import random
class Goal:
    def __init__(self,id,x,y,value):
        self.id = id
        self.x = x
        self.y = y
        self.value = value

    def set_random_goal(self, x_max, y_max):
        self.x = random.randint(10, x_max-10)
        self.y = random.randint(10, y_max-10)
        self.value = random.random()
