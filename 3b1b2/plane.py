import numpy as np
# import matplotlib as mpl
import matplotlib.pyplot as plt
# import moviepy.video.io.ImageSequenceClip

def map_torus_angle(alpha1,beta,alpha2):
    R=np.sin(beta)
    P=np.cos(beta)
    radius=R+P*np.sin(alpha2)
    return radius*np.cos(alpha1), radius*np.sin(alpha1), P*np.cos(alpha2)

def map_torus_point(x,y,z,w,beta=np.pi/4):
    R=np.sin(beta)
    return x*(1+w/R), y*(1+w/R), z

def test(a,b,c,d):
    vec = np.array([[a+1j*b, c+1j*d]])

    r1 = np.abs(vec[0,0])
    ang1 = np.angle(vec[0,0])

    r2 = np.abs(vec[0,1])
    ang2 = np.angle(vec[0,1])

    print("z1:",r1.round(3),"/_",ang1*180/np.pi," deg")
    print("z1:",r2.round(3),"/_",ang2*180/np.pi," deg")

    C = (r1**2 + r2**2)
    print("C = r1^2 + r2^2 = ", C.round(3))
    beta = np.arcsin(r1/np.sqrt(C))
    print("beta=",beta)

    theta1 = np.pi/6
    theta6 = np.pi/4

    alpha1 = ang1 + theta1
    alpha2 = ang2 + theta6

    P = r1 + np.sqrt(C)*r2*np.sin(alpha2)
    v = np.exp(1j*alpha1)
    R = P*v
    print([R.real,R.imag,r2*np.cos(alpha2)])

    cm = np.array([
        [np.exp(1j*theta1),0],
        [0,np.exp(1j*theta6)]
    ])

    rot = np.einsum('ij...,kj...->i...', cm, vec, optimize = True)
    rot = np.array([rot[0].real, rot[0].imag, rot[1].real, rot[1].imag])
    x,y,z = map_torus_point(*rot,beta = beta)
    print(x,y,z)

# test(1,0,2,4)

def surface_rot(time):
    space = np.arange(-np.pi/2,np.pi/2,0.005)
    X,Y = np.meshgrid(space,space)
    Z,W = np.meshgrid(space,space)
    X = 0.5*X
    Y = Y
    Z = 1.5*Z
    W = W
    
    theta = lambda t,x,y,z,w : 0.03*t + 0.3*x + 0.8*y + 1*w - 1*z
    phi = lambda t,x,y,z,w : 0.03*t + 0.3*x + 0.8*y + 1*w - 0.5*z

    vector = np.array([[X+Y*1j,Z+W*1j]]) # XY plane only

    beta =  np.arcsin(np.sqrt(X**2 + Y**2)/np.sqrt(X**2 + Y**2 + Z**2 + W**2))

    plt.figure()
    plt.imshow(beta)
    plt.show()
    fig = plt.figure()
    ax_3D = fig.add_subplot(1,1,1, projection="3d")
    for i in range(0,time):
        t = i*np.ones_like(X)

        complex_matrix = np.array([
            [np.exp(1j*theta(t,X,Y,Z,W)), np.zeros_like(X)],
            [np.zeros_like(X) , np.exp(1j*phi(t,X,Y,Z,W))]
        ],dtype="complex")
        # rotation and plotting on torus using hopf map
        rot = np.einsum('ij...,kj...->i...', complex_matrix,vector, optimize = True)
        rot = np.array([rot[0].real, rot[0].imag, rot[1].real, rot[1].imag])
        x,y,z = map_torus_point(*rot,beta = beta)
        # plotting

        # ax_3D.plot_surface(X,Y,Z)
        ax_3D.plot_surface(x,y,z,linewidth=5,antialiased=True,alpha=0.7,edgecolor='none',cmap=plt.cm.Spectral )
        # ax_3D.plot_surface(rot[0],rot[1],rot[2],linewidth=5,antialiased=True,alpha=0.7,edgecolor='none',cmap=plt.cm.Spectral )
        # ax_3D.plot_surface(rot[0],rot[1],rot[3],linewidth=5,antialiased=True,alpha=0.7,edgecolor='none',cmap=plt.cm.Spectral )
        # ax_3D.plot_surface(rot[0],rot[2],rot[3],linewidth=5,antialiased=True,alpha=0.7,edgecolor='none',cmap=plt.cm.Spectral )
        plt.pause(0.01)
        if i < time-1: 
            ax_3D.clear()
    plt.show()

# surface_rot(100)