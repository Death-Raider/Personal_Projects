import numpy as np
from numpy import pi

radius_body = 4 # r
radius_leg_mov = 1.1 # l
mov_dir = pi/6 # d
mount_angles = np.array([i*pi/3 for i in range(6)]) # m
line_eq = lambda x,y,a: y-a*x # L

#leg pos calc
leg_angles_1 = np.array([-2.02*pi/7, pi, 8*pi/7]) # values gotten outta my ass
leg_angles_2 = 2*mov_dir - leg_angles_1
leg_pos_angle = np.array([ # m0
    leg_angles_1[0],
    leg_angles_2[0],
    leg_angles_1[1],
    leg_angles_1[2],
    leg_angles_2[2],
    leg_angles_2[1]
])
# p0
leg_pos = { 'x':radius_leg_mov*np.cos(leg_pos_angle), 'y': radius_leg_mov*np.sin(leg_pos_angle) }

# leg dir calc
leg_dir_angles_1 = pi*np.array([3/7, 1/6, 2/5]) # values gotten outta my ass
leg_dir_angles_2 = 2*mov_dir - leg_dir_angles_1
leg_dir = np.array([  # a
    leg_dir_angles_1[0],
    leg_dir_angles_2[0],
    leg_dir_angles_1[1],
    leg_dir_angles_1[2],
    leg_dir_angles_2[2],
    leg_dir_angles_2[1]
])

# calc leg dir points
# solution to Quadratic x^2 + (tan(a)(x-p0.x)+p0.y)^2 = l^2
# D^2 = l^2(1+tan^2(a)) - L(p0.x,p0.y)^2 
# x =  ( -tan(a)L(p0.x,p0.y) +/- D ) / (1+tan^2(a))
# y = tan(a)(x - p0.x) + p0.y
leg_dir_slope = np.tan(leg_dir)
D_seq = radius_leg_mov**2 * (1+leg_dir_slope**2) - line_eq(leg_pos['x'],leg_pos['y'],leg_dir_slope)**2
Lx1 = ( -leg_dir_slope*line_eq(leg_pos['x'],leg_pos['y'],leg_dir_slope) - np.sqrt(D_seq) ) / (1+leg_dir_slope**2)
Lx2 = ( -leg_dir_slope*line_eq(leg_pos['x'],leg_pos['y'],leg_dir_slope) + np.sqrt(D_seq) ) / (1+leg_dir_slope**2)
Ly1 = leg_dir_slope*(Lx1 - leg_pos['x']) + leg_pos['y']
Ly2 = leg_dir_slope*(Lx2 - leg_pos['x']) + leg_pos['y']

# start and end point for forward movement
leg_dir_pnt_start = np.array([*zip(Lx1,Ly1)])
leg_dir_pnt_end = np.array([*zip(Lx2,Ly2)])
# stride angle
mag_1 = np.hypot(leg_dir_pnt_end[:,0],leg_dir_pnt_end[:,1])
mag_2 = np.hypot(leg_dir_pnt_start[:,0],leg_dir_pnt_start[:,1])
phi = (leg_dir_pnt_end*leg_dir_pnt_start).sum(axis=1) / (mag_1 * mag_2)
phi = np.arccos(phi)



