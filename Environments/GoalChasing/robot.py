from Environments.GoalChasing.goal import Goal

import random
import numpy as np

class Robot:
    def __init__(self, id: int, x:float = 0, y:float = 0, h:float = 1, w:float = 1, a:float = 0, v:float = 0, dir:int = 0, cooperation: int = 1, closeness_threshold: int = 3):
        self.id = id
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.a = a
        self.v = v
        self.dir: int = dir # [NE, N, NW, E, W ,SE, S, SW] -> [135, 90, 45, 180, 0, 225, 270, 315]
        self.cooperation = cooperation
        self.closeness_threshold = closeness_threshold
        self.view = np.zeros((self.closeness_threshold*2+1, self.closeness_threshold*2+1))
        self.dist_view = self.view.copy()
        self.angle_view = self.view.copy()
        self.detected_robots: dict[str,list[int | tuple | Robot]] = {
            'id':[],
            'pos':[],
            'robot':[]
        }
        self.DIR_ANGLES = [135, 90, 45, 180, 0, 225, 270, 315]

    def move(self,x_max,y_max):
        #           [NE,  N, NW,  E, W, SE, S, SW]
        row_order = [-1, -1, -1,  0, 0,  1, 1, 1] # Y
        col_order = [-1,  0,  1, -1, 1, -1, 0, 1] # X

        vx = self.v*col_order[self.dir]
        vy = self.v*row_order[self.dir]
        new_x = self.x + vx
        new_y = self.y + vy
        if (0 <= new_x < x_max) and (0 <= new_y < y_max):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def detect_robots(self):
        (r,c) = np.where((self.view != 0) & (self.view != self.id))
        if len(r)==0: # reset the detected robots folder
            for key in self.detected_robots.keys():
                self.detected_robots[key] = []
        else: # populate the detected robots folder
            ids_copy = set(self.detected_robots['id'].copy())
            new_ids = set()
            for x in zip(r,c):
                id = int(self.view[x[0],x[1]])
                pos = [
                    np.hypot(x[0]-self.closeness_threshold, x[1]-self.closeness_threshold),
                    self._set_angle(self.closeness_threshold, self.closeness_threshold, *x)
                ]
                # pos = self.get_dist(x)  # error
                if id < 0:
                    continue
                new_ids.add(id)
                if id not in self.detected_robots['id']:
                    self.detected_robots['id'].append(id)
                    self.detected_robots['pos'].append(pos)
                    self.detected_robots['robot'].append(None)
                else:
                    index = self.detected_robots['id'].index(id)
                    self.detected_robots['id'][index] = id
                    self.detected_robots['pos'][index] = pos

            ids_to_remove = ids_copy.difference(new_ids) # get ids which are not in the update view
            for id in ids_to_remove: # remove them
                index = self.detected_robots['id'].index(id)
                for key in self.detected_robots.keys():
                    self.detected_robots[key].pop(index)

    def get_DQL_state(self, goal: Goal):
        self.dist_view = self.view.copy()
        self.angle_view = np.zeros_like(self.view)
        (r,c) = np.where(self.view != 0)
        
        for x in zip(r,c):
            id = int(self.view[x[0],x[1]])
            if id < 0:
                continue
            if id == self.id:
                self.angle_view[x[0],x[1]] = self.DIR_ANGLES[self.dir] * np.pi/180
                self.dist_view[x[0],x[1]] = 0
            else:
                index = self.detected_robots['id'].index(id)
                other_dir = self.detected_robots['robot'][index].dir
                self.angle_view[x[0],x[1]] = self.DIR_ANGLES[other_dir] * np.pi/180
                self.dist_view[x[0],x[1]] = self.get_dist(self.detected_robots['robot'][index])[0]
    
        # Add relative goal position (dx, dy) and wall proximity
        goal_dx = goal.x - self.x  # Assuming `self.goal` is accessible
        goal_dy = goal.y - self.y
        
        # Flatten and concatenate features
        view_features = np.array([self.dist_view, self.angle_view]).flatten()
        goal_features = np.array([goal_dx, goal_dy])
        
        return np.concatenate([view_features, goal_features])

    def set_random_init_state(self, max_x, max_y):
        self.x = random.randint(0,max_x-1)
        self.y = random.randint(0,max_y-1)
        self.v = 2*random.random()
        self.dir = random.randint(0,7)

    def get_dist(self, other):
        if isinstance(other, Robot) or isinstance(other, Goal):
            x = other.x
            y = other.y
        elif isinstance(other, list) or isinstance(other, tuple):
            x = other[1]
            y = other[0]
        else:
            raise ValueError("Operand not of type list or Robot.")
        dist = np.hypot(self.x - x, self.y - y)
        angle = self._set_angle(self.y,self.x, y,x)
        return dist, angle
    
    def _set_angle(self, y1,x1, y2,x2):
        angle = np.arctan2(y1 - y2, x2 - x1)
        if angle < 0:
            angle += 2*np.pi
        return angle
    
    def _set_dir(self, ind):
        assert -1 < ind < 8
        self.dir = ind

    def object_avoidance_deviation_calculation(self):
        deviation_angle = 2 # for example
        self.dir = deviation_angle
        return deviation_angle

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
