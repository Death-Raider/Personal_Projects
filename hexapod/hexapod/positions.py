"""
Class to implement custom datatype to incorporate the movement data

positions = {
    <leg_index> : [
        {
            "plane_point":plane_point,
            "angle":[theta1,theta2],
            "mount_angle": mount_ang,
            "mount_rot": mount_rot
        },
        {
            "plane_point":plane_point,
            "angle":[theta1,theta2],
            "mount_angle": mount_ang,
            "mount_rot": mount_rot
        }, 
        {
            "plane_point":plane_point,
            "angle":[theta1,theta2],
            "mount_angle": mount_ang,
            "mount_rot": mount_rot
        },
        ... n
    ], 
    ... 
}
"""
import json
class Position:
    def __init__(self, smoothness):
        self.smoothness = smoothness
        self.leg_indicies = []
        self.plane_points = []
        self.angle = []
        self.mount_angle = []
        self.mount_rot = []
        self.pos = {}
    
    def __getitem__(self,index:str|tuple[str])->dict[list] | list:
        if isinstance(index, str):
            out = dict()
            for i in self.leg_indicies:
                leg = self.pos[i]
                out[i] = [data[index] for data in leg]

        elif isinstance(index,tuple):
            if len(index) == 2:
                leg = self.pos[index[0]]
                out = [data[index[1]] for data in leg]
            else:
                leg = self.pos[index[0]]
                out = [
                    [data[atr] for data in leg]
                    for atr in index[1:]
                ]
        
        else:
            raise KeyError("unknown key type")

        return out
    

    def add_point(self, leg_index, plane_point, angle, mount_angle, mount_rot):
        if leg_index not in self.pos.keys():
            self.leg_indicies.append(leg_index)
            self.pos[leg_index] = []

        self.pos[leg_index].append({
            "plane_point": plane_point,
            "angle": angle,
            "mount_angle": mount_angle,
            "mount_rot": mount_rot
        })
    
    def update_leg(self, leg_index, data):
        self.pos[leg_index] = data

    def add_leg(self, leg_index, data):
        def update(k,data):
            if k in self.pos.keys():
                self.update_leg(k, data)
            else:
                self.leg_indicies.append(k)
                self.pos[k] = data

        if isinstance(data, Position):
            for k in data.pos.keys():
                update(k,data.pos[k])
        else:
            update(leg_index, data)
    
    def reset(self, smoothness):
        self.smoothness = smoothness
        self.leg_indicies = []
        self.plane_points = []
        self.angle = []
        self.mount_angle = []
        self.mount_rot = []
        self.pos = {}
    
    def copy(self):
        """
            Makes a copy of itself with the catch that all keys are strings
        """
        new_pos = Position(self.smoothness)
        new_pos.leg_indicies = self.leg_indicies.copy()
        new_pos.plane_points = json.loads(json.dumps(self.plane_points))
        new_pos.angle = json.loads(json.dumps(self.angle))
        new_pos.mount_angle = json.loads(json.dumps(self.mount_angle))
        new_pos.mount_rot = json.loads(json.dumps(self.mount_rot))
        new_pos.pos = json.loads(json.dumps(self.pos))
        return new_pos