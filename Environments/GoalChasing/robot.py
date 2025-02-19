from Environments.GoalChasing.goal import Goal

import random
import numpy as np

class Robot:
    def __init__(self, id: int, x:float = 0, y:float = 0, a:float = 0, v:float = 0, dir:float = 0, cooperation: int = 1):
        self.id = id
        self.x = x
        self.y = y
        self.a = a
        self.v = v
        self.dir = dir # angle in radians from the x axis
        self.cooperation = cooperation
        self.closeness_threshold = 3
        self.view = np.zeros((self.closeness_threshold*2+1, self.closeness_threshold*2+1))
        self.detected_robots: dict[str,list] = {
            'id':[],
            'pos':[],
            'robot':[]
        }

    def move(self):
        vx = self.v*np.cos(self.dir)
        vy = self.v*np.sin(self.dir)
        self.x += vx
        self.y += vy
    
    def detect_robots(self)->list[tuple]:
        (r,c) = np.where((self.view != 0) & (self.view != self.id))
        if len(r)==0: # reset the detected robots folder
            for key in self.detected_robots.keys():
                self.detected_robots[key] = []
        else: # populate the detected robots folder
            ids_copy = self.detected_robots['id'].copy()
            for x in zip(r,c):
                id = int(self.view[*x])
                pos = self.get_dist(x)
                if id < 0:
                    continue
                if id not in self.detected_robots['id']:
                    self.detected_robots['id'].append(id)
                    self.detected_robots['pos'].append(pos)
                    self.detected_robots['robot'].append(None)
                else:
                    # ids_copy.remove(id)
                    index = self.detected_robots['id'].index(id)
                    self.detected_robots['id'][index] = id
                    self.detected_robots['pos'][index] = pos
            # if len(ids_copy) > 0 and len(self.detected_robots['id']) > 0:
            #     self.detected_robots['id'].remove(ids_copy)

    def set_dir(self, goal):
        goal_distance, goal_angle = self.get_dist([goal.y,goal.x])
        self.dir = goal_angle
        print(self.id, self.detected_robots)

    def object_avoidance_deviation_calculation(self):
        """
            Returns the deviation angle for the robot's direction from the optimal path.
            This function can be replaced by a DQL agent to return the angle as an action.
            Angle "a" is a float from 0 to 2*pi and for calculations can be used as an int from 0 to 360.
            
            We can also use another action space (8 movements corresponding to the possible pixel movements)
            ----------------
            | ul |  u | ur |
            ----------------
            |  l |  x |  r |
            ----------------
            | dl |  d | dr |
            ----------------
            if the goal direction path exists from current pos then we want to move to the pixel which follows that path
            We can add a reward/punishment for deviation based on current state of the "view" and "detected_robots".
            This can also quantize direction into 8 values but then direction is more dynamic for intermediate values like 110 degrees
            r = 0/360
            ur = 45
            u = 90
            ul = 135
            l = 180
            dl = 225
            d = 270
            dr = 315

        """
        # check the states of the robots which are close
        # determine deviation angle 
        deviation_angle = 0.2 # for example

        # ---- hard coded logic part ----
        # calculate estimated point of intersection
        # if the intersection point lies on the line of self to self goal then do
            # calculate time to intersection for both the robots
            # if time is within threshold then do
                # choose to do one of the following
                # 1. slow down
                # 2. speed up
                # 3. add a deviation angle to recompute for next step
            # else
                # the robots will not clash
        # else
            # skip the robot as it is just close but not in the way
        #
        # ---- Q Learning part ----
        # calculate deviation angle by q learning 
        self.dir = self.dir + deviation_angle
        return deviation_angle

    def set_random_init_state(self, max_x, max_y):
        self.x = random.randint(0,max_x-1)
        self.y = random.randint(0,max_y-1)
        self.v = 2*random.random()
        self.dir = random.random()

    def get_dist(self, other):
        if isinstance(other, Robot):
            x = other.x
            y = other.y
        elif isinstance(other, list) or isinstance(other, tuple):
            x = other[1]
            y = other[0]
        else:
            raise ValueError("Operand not of type list or Robot.")
        dist = np.hypot(self.x - x, self.y - y)
        angle = np.arctan2(y - self.y, x - self.x)
        if angle < 0:
            angle += 2*np.pi
        return dist, angle

    def __str__(self):
        return f"Robot id: {self.id}"

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
