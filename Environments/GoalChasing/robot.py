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

    def move(self):
        vx = self.v*np.cos(self.dir)
        vy = self.v*np.sin(self.dir)
        self.x += vx
        self.y += vy
    
    def set_dir(self, goal, player_dist_vector):
        goal_distance, goal_angle = self.get_dist([goal.y,goal.x])
        self_index = np.where(player_dist_vector[:,0]==0)[0][0]

        goal_based_relative_angle = player_dist_vector[:,1] - goal_angle # alpha
        goal_based_relative_angle = np.where(goal_based_relative_angle < 0, goal_based_relative_angle + np.pi*2, goal_based_relative_angle)

        close_robot_indicies = np.where(player_dist_vector[:,0] <= self.closeness_threshold)[0] # robots which are close to self
        # print(f"Robot {self.id}:", close_robot_indicies )

        if len(close_robot_indicies) == 1:
            self.dir = goal_angle
        else:   
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
            self.dir = goal_angle + deviation_angle


    def set_random_init_state(self, max_x, max_y):
        self.x = random.randint(0,max_x-1)
        self.y = random.randint(0,max_y-1)
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
