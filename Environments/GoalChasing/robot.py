from Environments.GoalChasing.goal import Goal

import random
import numpy as np

class Robot:
    def __init__(self, id: int, x:float = 0, y:float = 0, a:float = 0, v:float = 0, dir:int = 0, cooperation: int = 1):
        self.id = id
        self.x = x
        self.y = y
        self.a = a
        self.v = v
        self.dir: int = dir # [NE, N, NW, E, W ,SE, S, SW] -> [135, 90, 45, 180, 0, 225, 270, 315]
        self.cooperation = cooperation
        self.closeness_threshold = 3
        self.view = np.zeros((self.closeness_threshold*2+1, self.closeness_threshold*2+1))
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
                    self._set_angle(*x, self.closeness_threshold, self.closeness_threshold)
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

    def get_DQL_state(self, goal: Goal, board_size):
        position_view = self.view.copy()
        angle_view = self.view.copy()
        (r,c) = np.where(self.view != 0)
        
        for x in zip(r,c):
            id = int(self.view[x[0],x[1]])
            if id < 0:
                continue
            if id == self.id:
                angle_view[x[0],x[1]] = self.DIR_ANGLES[self.dir] * np.pi/180
            else:
                index = self.detected_robots['id'].index(id)
                other_dir = self.detected_robots['robot'][index].dir
                angle_view[x[0],x[1]] = self.DIR_ANGLES[other_dir] * np.pi/180
    
        # Add relative goal position (dx, dy) and wall proximity
        goal_dx = goal.x - self.x  # Assuming `self.goal` is accessible
        goal_dy = goal.y - self.y
        wall_proximity = [
            self.x < self.closeness_threshold,                   # Near left wall
            self.y < self.closeness_threshold,                   # Near top wall
            (board_size - self.x) < self.closeness_threshold,    # Near right wall
            (board_size - self.y) < self.closeness_threshold     # Near bottom wall
        ]
        
        # Flatten and concatenate features
        view_features = np.array([position_view, angle_view]).flatten()
        goal_features = np.array([goal_dx, goal_dy])
        wall_features = np.array(wall_proximity, dtype=np.float32)
        
        return np.concatenate([view_features, goal_features, wall_features])

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
        # angle = np.arctan2(y - self.y, x - self.x)
        # if angle < 0:
        #     angle += 2*np.pi
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
        
if __name__ == '__main__':

    r1 = Robot(
        id=1,
        x=2,
        y=1,
        a=0,
        v=1,
        dir=[0,0,1,0,0,0,0,0]
    )
    r2 = Robot(
        id=2,
        x=2,
        y=1,
        a=0,
        v=1,
        dir=[0,0,0,0,0,1,0,0]
    )
    r1.move(10,10)
    print(r1.x,r1.y)
    r1.view[r1.closeness_threshold,r1.closeness_threshold] = 1
    r1.view[r1.closeness_threshold+1,r1.closeness_threshold] = 2
    r1.detect_robots()
    r1.detected_robots['robot'][0] = r2
    print(r1.detected_robots)
    print(r1.view)
    print(r1.get_DQL_state().reshape((2,7,7)))