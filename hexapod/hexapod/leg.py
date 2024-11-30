# from hexapod.rotation import Rotation
from rotation import Rotation
import numpy as np
import math
from positions import Position
class Leg:
    def __init__(self,leg_id, leg_name):
        self.id = leg_id
        self.name = leg_name
        self.lengths = [0.25, 0.5, 1] # [leg_mount to joint_1, joint_1 to joint_2, joint_2 to feet]
        self.mount_dir = [1.0, 0.0, 0.0] # leg mounted in this direction [x,y,z]
        self.joints = list(map(lambda x: f"{self.name}_{x}", ['mount', 'joint_1', 'joint_2', 'feet']))
        self.joints_pos = [[0.0]*3 for i in self.joints]
        self.joints_rot = [[0.0, 0.0, 0.0, 1.0] for i in self.joints]
        self.joints_angle = [[0.0]*3 for i in self.joints]
        self.rotation = Rotation()
        self.pos = Position(0)
    
    def init_leg(self):
        # initially leg is flat in the mount direction
        data = []
        for i in range(1, len(self.joints)):
            self.joints_pos[i] = [self.lengths[i-1]*1.0, 0.0, 0.0]
            data.append({
                'parent_name' : self.joints[i-1],
                'child_name': self.joints[i],
                'child_pos' : self.joints_pos[i],
                'child_rot' :  self.joints_rot[i]
            })
        return data
    
    def get_absolute_joint_position(self):
        self.joints_abs_pos = [[0.0]*3 for i in self.joints_pos]
        self.joints_abs_angle = [[0.0]*3 for i in self.joints_pos]
        self.joints_abs_pos[0] = self.joints_pos[0].copy()
        self.joints_abs_angle[0] = self.joints_angle[0].copy()
        for i in range(1,len(self.joints_pos)):
            self.joints_abs_angle[i] = self.joints_angle[i].copy()
            self.joints_abs_angle[i][0] += self.joints_abs_angle[i-1][0]
            self.joints_abs_angle[i][1] += self.joints_abs_angle[i-1][1]
            self.joints_abs_angle[i][2] += self.joints_abs_angle[i-1][2]
            self.joints_abs_pos[i] = self.rotation.rotate_point(*self.joints_pos[i],*self.joints_abs_angle[i-1])
            self.joints_abs_pos[i][0] += self.joints_abs_pos[i-1][0]
            self.joints_abs_pos[i][1] += self.joints_abs_pos[i-1][1]
            self.joints_abs_pos[i][2] += self.joints_abs_pos[i-1][2]

    def get_leg_movement(self,start_foot_pos, final_foot_pos, stride_time, max_height=1):
        
        def movement_function(x:float, vec:list[float], max_height:float = 1)->float:
            mag = math.hypot(*vec)
            return -4*max_height*(x/mag)**2+4*max_height*x/mag # returns the height
        
        def projected_movement(x:float, y:float, vec:list[float], max_height:float = 1)->float:
            mag = math.hypot(*vec)
            return movement_function( np.dot(vec,(x,y))/mag , vec, max_height)
        
        def movement_plane_movement(t:float, vec:list[float], max_height:float = 1)->tuple[float]:
            ratio = vec[1]/vec[0]  # y/x
            proj_mov = projected_movement(t, ratio*t, vec, max_height)
            return [t, ratio*t, proj_mov]
        
        diff_vec = [final_foot_pos[0] - start_foot_pos[0] , final_foot_pos[1] - start_foot_pos[1]]
        cond = diff_vec[0] < 0
        t_start = min(0,diff_vec[0])
        t_end = max(0,diff_vec[0])
        pos = []
        for t in np.linspace(t_start, t_end, stride_time):
            f_dash = movement_plane_movement(t,diff_vec,max_height)
            curr_foot_position = np.sum([start_foot_pos,f_dash],axis=0)
            pos.append(curr_foot_position)
        pos = np.array(pos)
        if cond:
            pos = pos[::-1]
        return pos

    def move_leg(self, mount_base_pos:list[float], stride_angle:float, smoothness:int, max_height:float, slide:bool=False)->Position:

        def leg_plane_x(theta:float,phi:float):
            """
            returns the distance between the chord and the corresponding sector of angle "phi" with a unit radius at an angle "theta" 
            """
            x = math.cos(phi/2)/math.cos(theta - phi/2)
            return x

        phi = stride_angle
        steps = smoothness
        self.pos.smoothness = smoothness
        max_height = 0.5
        # get foot and rotate it about mount by phi
        self.get_absolute_joint_position()
        init_foot_pos = self.joints_abs_pos[-1].copy()
        final_pos_foot = self.rotation.rotate_about_point(*self.joints_abs_pos[-1],*self.joints_abs_pos[0],0,0,phi)
        mount_ang = self.joints_angle[0].copy()
        # get the path that the foot should take
        path_pos = self.get_leg_movement(init_foot_pos,final_pos_foot,steps,max_height)
        # out_pos = np.zeros((steps,4)).tolist()
        for t in range(0, steps):
            x_1 =  leg_plane_x((t+1)*phi/steps, phi)
            plane_point = [x_1, path_pos[t][2] - path_pos[0][2]] # x position for foot, height of movement
            if slide:
                plane_point[1] = 0
            theta1,theta2 = self.rotation.inverse_kinematics(plane_point,mount_base_pos,self.lengths[1],self.lengths[2])
            # update mount angle by phi, get foot
            mount_ang[2] += phi/steps  # only updated mount in z axis, other joints y axis
            mount_rot = self.rotation.euler_to_quaternion(*mount_ang)
            self.pos.add_point(self.id,plane_point,[theta1,theta2],mount_ang,mount_rot)
        return self.pos