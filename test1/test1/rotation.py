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