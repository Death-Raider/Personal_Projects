import math

class Rotation:
    def __init__(self):
        pass

    def rotate_point(self, x, y, z, roll, pitch, yaw): # roll, pitch, yaw in radians
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        cp = math.cos(pitch)
        sp = math.sin(pitch)
        cr = math.cos(roll)
        sr = math.sin(roll)
        m11 = cy * cp
        m12 = cy * sp * sr - sy * cr
        m13 = cy * sp * cr + sy * sr
        m21 = sy * cp
        m22 = sy * sp * sr + cy * cr
        m23 = sy * sp * cr - cy * sr
        m31 = -sp
        m32 = cp * sr
        m33 = cp * cr
        x_new = m11 * x + m12 * y + m13 * z
        y_new = m21 * x + m22 * y + m23 * z
        z_new = m31 * x + m32 * y + m33 * z
        return [x_new, y_new, z_new]

    def euler_to_quaternion(self,roll, pitch, yaw):
        """
        Convert Euler angles to a quaternion.
        
        :param roll: Rotation about the x-axis (in radians)
        :param pitch: Rotation about the y-axis (in radians)
        :param yaw: Rotation about the z-axis (in radians)
        """
        # Compute the trigonometric functions once (based on half angles)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        # Compute the quaternion components
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return [x,y,z,w]
    
    def normalize(self,x,y,z):
        norm = math.hypot(x,y,z)
        return [x/norm, y/norm, z/norm]
    
    def scale(self,s,x,y,z):
        return [x*s, y*s, z*s]
    
    def polar(self,x,y):
        return [math.hypot(x,y), math.atan2(y,x)]
    
    def polar_about(self,x,y, px,py):
        return [math.hypot(x-px,y-py), math.atan2(y-py,x-px)]
    
    def inverse_kinematics(self, end_pos:list[float], base_pos:list[float], l1:float, l2:float):
        # inverse kinematics function for a robotic arm of 2 joints
        # joint  at base_pos
        # joint 2 at distance l1 from joint 1
        # feet at distance l2 from joint 2
        end_angles = [0,0] # theta1 and theta 2

        # displacement vector
        diff_vec = [end_pos[0] - base_pos[0], end_pos[1] - base_pos[1]]
        d = math.hypot(*diff_vec)

        # check if reachable 
        if d > l1+l2 or d < abs(l1 - l2):
            raise ValueError("Rotation IK: end position not reachable")
        
        # intermediate value calculation
        q = (l1**2 - l2**2 + d**2)/(2*l1*d)
        alpha = math.atan2(diff_vec[1],diff_vec[0])

        #calculate angles
        end_angles[0] = math.acos(q) + alpha
        end_angles[1] = math.asin( (diff_vec[1] - l1*math.sin(end_angles[0]))/l2 )
        return end_angles
    
    def rotate_about_point(self,x,y,z,px,py,pz,roll,pitch,yaw):
        x1,y1,z1 = x-px, y-py, z-pz
        x2,y2,z2 = self.rotate_point(x1,y1,z1,roll,pitch,yaw)
        x3,y3,z3 = x2+px, y2+py, z2+pz
        return [x3,y3,z3]
