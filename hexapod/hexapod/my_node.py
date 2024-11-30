#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np
import time
import math

# uncomment when building
# from hexapod.rotation import Rotation
# from hexapod.transformManager import TransformManager
# from hexapod.leg import Leg
# from hexapod.keyboardInput import KeyboardInput
# from hexapod.body import Body


# comment out when building 
from rotation import Rotation
from transformManager import TransformManager
from leg import Leg
from keyboardInput import KeyboardInput
from body import Body
from positions import Position

class TransformPublisher(Node):
    def __init__(self,node_name):
        super().__init__(node_name)

        self.transform_manager_static = TransformManager(node_cls = self, type = 'static')
        self.transform_manager_dynamic = TransformManager(node_cls = self, type = 'dynamic')
        self.rotation = Rotation()
        self.key_input = KeyboardInput()
        self.body = Body()
        self.legs = [Leg(i,f"leg_{i}") for i in range(6)] # create 6 legs
        self.init_body()
        self.stand_body()
        print("Body ready!")
        self.key_input.keyListener(self.movement)
        # self.timer = self.create_timer(0.1, self.stand_body)

    def get_timestamp(self):
        return self.get_clock().now().to_msg()

    def init_body(self): # lay flat on the floor
        # Set the body position of rover
        # B(1,0,0.5)
        self.transform_manager_static.set_transform('world','body',self.body.pos+self.body.rot, self.get_timestamp() )
        self.transform_manager_static.broadcast_transform()
        # Set the leg_mounts around the body of the rover in circle assuming B is origin
        init_dir = [1.0, 0.0, 0.0]
        angle = 0.0
        for i in range(6):
            mount_pos = self.rotation.rotate_point(*init_dir, 0.0, 0.0, angle) # rotate init_dir in increments of 120 deg
            self.legs[i].mount_dir = mount_pos
            # mount the leg in this direction
            self.legs[i].joints_angle[0] = [0.0, 0.0, angle]
            self.legs[i].joints_pos[0] = self.rotation.scale(self.body.radius, *mount_pos)
            self.legs[i].joints_rot[0] = self.rotation.euler_to_quaternion(*self.legs[i].joints_angle[0])
            # set the body and leg transforms
            self.transform_manager_static.set_transform('body', self.legs[i].joints[0], self.legs[i].joints_pos[0]+self.legs[i].joints_rot[0], self.get_timestamp())
            self.transform_manager_static.broadcast_transform()
            # initilize the rest of the leg
            leg_details = self.legs[i].init_leg()
            for data in leg_details:
                self.transform_manager_static.set_transform(data['parent_name'], data['child_name'] , data['child_pos']+data['child_rot'], self.get_timestamp())
                self.transform_manager_static.broadcast_transform()
            angle += np.pi/3
            time.sleep(0.01)

    def stand_body(self):
        for i in range(0,6):
            theta1,theta2 = self.rotation.inverse_kinematics((1,0), (0,0.5), 0.5, 1.0)
            self.set_leg(i,theta1, theta2, self.transform_manager_static)
    
    def set_leg(self, i, theta1, theta2, transform_manager):
        transform_manager.set_transform(
            'body',
            self.legs[i].joints[0],
            self.legs[i].joints_pos[0]+self.legs[i].joints_rot[0],
            self.get_timestamp()
        )
        transform_manager.broadcast_transform()
        self.legs[i].joints_angle[1] = [0,-theta1,0]
        transform_manager.set_transform(
            self.legs[i].joints[0],
            self.legs[i].joints[1],
            self.legs[i].joints_pos[1]+self.rotation.euler_to_quaternion(0,-theta1,0),
            self.get_timestamp()
        )
        transform_manager.broadcast_transform()
        self.legs[i].joints_angle[2] = [0,theta2+theta1,0]
        transform_manager.set_transform(
            self.legs[i].joints[1],
            self.legs[i].joints[2],
            self.legs[i].joints_pos[2]+self.rotation.euler_to_quaternion(0,-theta2+theta1,0),
            self.get_timestamp()
        )
        transform_manager.broadcast_transform()

    def post_position_movement(self,pos: Position):
        leg_indicies: list[str] = [*pos.pos.keys()] 
        smoothness = pos.smoothness
        for s in range(smoothness):
            for Li in leg_indicies:
                leg_vals = pos[(Li,'angle', 'mount_angle', 'mount_rot')]
                Li = int(Li)
                theta1, theta2 = leg_vals[0][s]
                self.legs[Li].joints_angle[0] = leg_vals[1][s]
                self.legs[Li].joints_rot[0] = leg_vals[2][s]
                self.set_leg(Li,theta1,theta2,self.transform_manager_dynamic)
            time.sleep(1/smoothness) # makes every movement happen in excatly 1 sec

    def move_leg(self,leg_index:int, phi:float, smoothness:int, slide:bool = False):
        """
            Move a single leg by an angle phi with some smoothness
        """
        positions = self.legs[leg_index].move_leg([0,0.5], phi, smoothness, 0.5, slide=slide).copy()
        self.legs[leg_index].pos.reset(smoothness)
        return positions

    def move_legs(self, leg_indicies:list[int], phi:float, smoothness:int, slide:bool = False):
        """
            Move a list of legs by an angle phi with some smoothness.
            All legs will move toegther
        """
        leg_pos = Position(smoothness)
        MAX_HEIGHT=0.5
        for i in leg_indicies:
            data = self.legs[i].move_leg([0,0.5],phi,smoothness,MAX_HEIGHT,slide).copy()
            self.legs[i].pos.reset(smoothness)
            data = data.pos[str(i)]
            leg_pos.add_leg(str(i),data)
        return leg_pos
    
    def rotate(self,phi):
        L1 = [0,2,4]
        L2 = [1,3,5]
        phi1,phi2 = phi, -phi
        smoothness = 10

        pos_L1_forward = self.move_legs(L1,phi1,smoothness,False)
        self.post_position_movement(pos_L1_forward)

        pos_L2_forward = self.move_legs(L2,phi1,smoothness,False)
        pos_L1_backword = self.move_legs(L1,phi2,smoothness,True)
        pos_L2_forward.add_leg(None, pos_L1_backword)
        self.post_position_movement(pos_L2_forward)

        pos_L2_backword = self.move_legs(L2,phi2,smoothness,True)
        self.post_position_movement(pos_L2_backword)

    def forward(self,face:int):
        phi = []
        
        smoothness = 10

    def movement(self,char):
        if char == 'w':
            print("moved leg")
            pos = self.move_legs([0,2,4],0.53,10,False)
            self.post_position_movement(pos)
            pass
        elif char == 's':
            pos = self.move_legs([0,2,4],-0.53,10,True)
            self.post_position_movement(pos)
            print("moved leg")
            pass
        elif char == 'd':
            self.rotate(0.53)
        elif char == 'a':
            self.rotate(-0.53)
        else:
            self.stand_body()

def main(args=None):
    rclpy.init(args=args)
    node = TransformPublisher('hexapod_node')
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
