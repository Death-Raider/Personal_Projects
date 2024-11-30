from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from matplotlib import cm
import numpy as np
import os
import moviepy.video.io.ImageSequenceClip
def make_movie(size,fps):
    image_files = []
    for a in range(size):
        for b in range(size):
            image_files.append(f"Images/{a}_{b}.png")
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(f'animation@{fps}.mp4')
    return True

def animate(matrix,size,n):
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    a = np.linspace(-size,size,n)
    b = np.linspace(-size,size,n)*1j
    xx,yy = np.meshgrid(a,b)
    p = xx+yy
    p_r = p.real
    p_i = p.imag
    for la in range(len(b)):
        for mu in range(len(a)):

            x_0,y_0 = mu,la
            v = np.ndarray((len(a),len(a),2),dtype="complex")
            for i in range(len(p)):
                for j in range(len(p[i])):
                    v[j][i] = matrix.dot([p[j,i],p[x_0,y_0]])
            v0_abs = np.abs(v[:,:,0])
            v0_phase = normalize(np.angle(v[:,:,0]))
            v1_abs = np.abs(v[:,:,1])
            v1_phase = normalize(np.angle(v[:,:,1]))

            ax1.plot_surface(p_r, p_i, v0_abs, facecolors=cm.jet(v0_phase))
            ax1.set_title("v0")
            ax1.set_xlim3d(-size*2, size*2)
            ax1.set_ylim3d(-size*2, size*2)
            ax1.set_zlim3d(-40, 40)

            ax2.plot_surface(p_r, p_i,v1_abs, facecolors=cm.jet(v1_phase))
            ax2.set_title("v1")
            ax2.set_xlim3d(-size*2, size*2)
            ax2.set_ylim3d(-size*2, size*2)
            ax2.set_zlim3d(-40, 40)

            # plt.savefig(f"Images/{la}_{mu}.png", dpi=300)
            plt.pause(0.001)
            ax1.cla()
            ax2.cla()
def normalize(arr):
    arrMin = np.min(arr)
    arrMax = np.max(arr)
    arr = arr - arrMin
    return arr / (arrMax - arrMin)

matrix = np.array([
    [0 , -1+1j],
    [1+1j,  0]
])
animate(matrix,1,10)
# make_movie(50,20)
