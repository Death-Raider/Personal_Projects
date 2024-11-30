import numpy as np
import matplotlib.pyplot as plt
# import moviepy.video.io.ImageSequenceClip

def make_movie(size,fps):
    # image_files  = list(map(lambda a: f"Images/Rotation_{a}.png",np.arange(0,size)))
    # clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    # clip.write_videofile(f'animation@{fps}.mp4')
    return True

def map_torus_angle(alpha1,beta,alpha2):
    R = np.sin(beta)
    P = np.cos(beta)
    radius = R+P*np.sin(alpha2)
    return radius*np.cos(alpha1), radius*np.sin(alpha1), P*np.cos(alpha2)

def map_torus_point(x,y,z,w,beta=np.pi/4):
    R = np.sin(beta)
    return x*(1+w/R), y*(1+w/R), z

def rotation(m,v):
    complex_vector = np.array([v[0]+v[1]*1j, v[2]+v[3]*1j],dtype="complex")
    result = np.array([m[0]*complex_vector[0],m[1]*complex_vector[1]])
    result = np.array([result[0].real, result[0].imag, result[1].real, result[1].imag])
    return result

def plot_Torus(beta = np.pi/4, show=True,resolution=100):


    a1 = np.linspace(0, 2*np.pi, resolution)
    a2 = np.linspace(0, 2*np.pi, resolution)
    alpha1,alpha2 = np.meshgrid(a1,a2)
    x,y,z = map_torus_angle(alpha1,beta,alpha2)

    if show:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection = "3d")
        ax.title.set_text('Rotation Path')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_xlim3d(-1.5, 1.5)
        ax.set_ylim3d(-1.5, 1.5)
        ax.set_zlim3d(-1.0, 1.0)
        ax.plot_surface(x, y, z, cmap='viridis',alpha=0.5, linewidth=0)
        plt.show()
    return x,y,z

def plot_rotation_path(theta_0=0,
                        phi_0=0,
                        alpha1=np.random.rand()*2*np.pi,
                        alpha2=np.random.rand()*2*np.pi,
                        w1=1,
                        w2=1,
                        beta = np.pi/4,
                        resolution=500,
                        time = 1,
                        show=True):
    #constants

    vector = np.array([
        np.sin(beta)*np.sin(alpha1),
        np.sin(beta)*np.cos(alpha1),
        np.cos(beta)*np.sin(alpha2),
        np.cos(beta)*np.cos(alpha2)
    ])
    #rotation
    theta = w1*np.linspace(theta_0, time*2*np.pi, resolution)
    phi = w2*np.linspace(phi_0, time*2*np.pi, resolution)
    complex_matrix = np.array([np.e**(1j*theta),np.e**(1j*phi)],dtype="complex")
    rotated = rotation(complex_matrix,vector)
    #4d point on torus
    x_0,y_0,z_0 = map_torus_point(rotated[0,:], rotated[1,:], rotated[2,:], rotated[3,:], beta=beta)
    x,y,z = plot_Torus(beta=beta,show=False,resolution=resolution)

    if show:
        fig = plt.figure()
        ax_3D = fig.add_subplot(1,1,1, projection="3d")
        ax_3D.plot3D(x_0,y_0,z_0)
        ax_3D.plot_surface(x,y,z,cmap='viridis',alpha=0.5, linewidth=0)
        plt.show()
    return x_0,y_0,z_0

#fourier is that u?
def orthocenter_rotation_path(w1=1,
                    theta_0=0,
                    phi_0=0,
                    alpha1=np.random.rand()*2*np.pi,
                    alpha2=np.random.rand()*2*np.pi,
                    angle_multiplier=1,
                    winding_range=10,
                    winding_resolution = 100,
                    beta=np.pi/4,
                    save=False,
                    fps=5,
                    show=False):

    winding_frequency_range = np.linspace(0,winding_range,winding_resolution)
    O_x = []
    O_y = []
    O_z = []
    w1 = w1*angle_multiplier
    x,y,z = plot_Torus(beta=beta,show=False)

    if show or save:
        fig = plt.figure()
        ax_1 = plt.subplot2grid((5,6), (0,0), rowspan=2, colspan=3, projection = "3d")
        ax_2 = plt.subplot2grid((5,6), (0,4), rowspan=2, colspan=2)
        ax_x = plt.subplot2grid((10,1), (5,0), rowspan=1, colspan=1)
        ax_y = plt.subplot2grid((10,1), (7,0), rowspan=1, colspan=1)
        ax_z = plt.subplot2grid((10,1), (9,0), rowspan=1, colspan=1)

    for index,winding_frequency in enumerate(winding_frequency_range):

        x_0,y_0,z_0 = plot_rotation_path(w1=w1,w2=winding_frequency*angle_multiplier,beta=beta,show=False,resolution=500)

        #taking ortho center of x,y,z coordinates
        O_x.append( x_0.sum()/x_0.shape[0] )
        O_y.append( y_0.sum()/y_0.shape[0] )
        O_z.append( z_0.sum()/z_0.shape[0] )
        if save or show:

            ax_1.title.set_text('Rotation Path')
            ax_1.set_xlim3d(-1.5, 1.5)
            ax_1.set_ylim3d(-1.5, 1.5)
            ax_1.set_zlim3d(-1.0, 1.0)
            ax_1.plot_surface(x, y, z, cmap='viridis',alpha=0.5, linewidth=0);
            ax_1.plot3D(x_0,y_0,z_0)

            ax_2.title.set_text('xy projection')
            ax_2.plot(x_0,y_0)

            dist = np.sqrt(np.array(O_x)**2 + np.array(O_y)**2 )

            ax_x.title.set_text('X coordinate of Orthocenter')
            ax_x.plot(winding_frequency_range[0:len(O_x)],O_x)

            ax_y.title.set_text('Y coordinate of Orthocenter')
            ax_y.plot(winding_frequency_range[0:len(O_y)],O_y)

            ax_z.title.set_text('Distance of Orthocenter')
            ax_z.plot(winding_frequency_range[0:len(O_z)],dist)

            if save:
                plt.savefig(f"Images/Rotation_{index}.png", dpi=300)
            if show:
                plt.pause(0.01)
            ax_1.cla()
            ax_2.cla()
            ax_z.cla()
            ax_y.cla()
            ax_x.cla()

    if save:
        make_movie(winding_resolution,fps)
    return O_x,O_y,O_z

# orthocenter_rotation_path(w1=np.sqrt(7),winding_range=7*np.pi,winding_resolution=100,beta=np.pi/3,angle_multiplier=1,show=True,save=False)
# plot_rotation_path(show=True,beta=np.pi/3)
