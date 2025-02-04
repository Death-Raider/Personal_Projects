from goal import Goal

import random
import numpy as np

class Robot:
    def __init__(self, id: int, x:float = 0, y:float = 0, a:float = 0, v:float = 0, dir:float = 0):
        self.id = id
        self.x = x
        self.y = y
        self.a = a
        self.v = v
        self.dir = dir # angle in radians from the x axis

    def move(self):
        vx = self.v*np.cos(self.dir)
        vy = self.v*np.sin(self.dir)
        self.x += vx
        self.y += vy
    
    def set_random_init_state(self, max_x, max_y):
        self.x = random.randint(0,max_x)
        self.y = random.randint(0,max_y)
        self.v = 2*random.random()
        self.dir = random.random()

    def get_dist(self, other):
        if isinstance(other, Robot):
            x = other.x
            y = other.y
        elif isinstance(other, list):
            x = other[1]
            y = other[0]
        else:
            raise ValueError("Operand not of type list or Robot.")
        dist = np.hypot(self.x - x, self.y - y)
        angle = np.arctan2(y - self.y, x - self.x)
        if angle < 0:
            angle += 2*np.pi
        return dist, angle

    def __gt__(self, other):
        if isinstance(other, list):
           return (self.y > other[0], self.x > other[1])
        elif isinstance(other, int|float):
           return (self.y > other[0], self.x > other[1])
        elif isinstance(other, Robot):
            return (self.y > other.y, self.x > other.y)
        else:
            raise ValueError("Operand not of type list, int, float, or Robot.")

    def __lt__(self, other):
        if isinstance(other, list):
           return (self.y < other[0], self.x < other[1])
        elif isinstance(other, int|float):
           return (self.y < other[0], self.x < other[1])
        elif isinstance(other, Robot):
            return (self.y < other.y, self.x < other.y)
        else:
            raise ValueError("Operand not of type list, int, float, or Robot.")

    def __eq__(self, other):
        if isinstance(other, list):
           return (self.y == other[0], self.x == other[1])
        elif isinstance(other, int|float):
           return (self.y == other[0], self.x == other[1])
        elif isinstance(other, Robot):
            return (self.y == other.y, self.x == other.y)
        else:
            raise ValueError("Operand not of type list, int, float, or Robot.")

    def __add__(self,other: list|int|float):
        if isinstance(other, list):
            self.x += other[1]
            self.y += other[0]
        elif isinstance(other, int|float):
            self.x += other
            self.y += other
        else:
            raise ValueError("Operand not of type list, int or float.")
    
    def __sub__(self, other: list|int|float):
        if isinstance(other, list):
            self.x -= other[1]
            self.y -= other[0]
        elif isinstance(other, int|float):
            self.x -= other
            self.y -= other
        else:
            raise ValueError("Operand not of type list, int or float.")
