import matplotlib.pyplot as plt
import numpy as np

def rotation(v,n,angle):
    get_matrix_eq_vector = lambda n,B: n[0]*B[0] + n[1]*B[1] + n[2]*B[2]
    get_vector_eq_matrix = lambda m: np.array([ m[1,0].real, m[1,0].imag, m[0,0].real ])
    def rotate_matrix(plane,vector,angle):
        R = np.cos(angle/2)*np.array([[1,0],[0,1]]) + plane*np.sin(angle/2)
        R_ = np.cos(angle/2)*np.array([[1,0],[0,1]]) - plane*np.sin(angle/2)
        return np.matmul(R_,np.matmul(vector,R))

    pauli_basis = np.array([
        np.array([[0,1],[1,0]],dtype="complex"), # x basis
        np.array([[0,-1j],[1j,0]],dtype="complex"), # y basis
        np.array([[1,0],[0,-1]],dtype="complex") # z basis
    ])

    plane = get_matrix_eq_vector(n,pauli_basis)*1j
    vec = get_matrix_eq_vector(v,pauli_basis)
    new_vec = rotate_matrix(plane,vec,angle)
    return get_vector_eq_matrix(new_vec)


def show():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    vector = np.array([5,5,0])
    axis = np.array([1/np.sqrt(2),1/np.sqrt(2),0])

    print(rotation(vector,axis,np.pi) )
    vec_to_comp = lambda v: ( np.array([0,v[0]]), np.array([0,v[1]]), np.array([0,v[2]]) )

    for a in range(45):
        x1,y1,z1 = vec_to_comp(axis)
        ax.scatter(x1,y1,z1,color="black")
        ax.plot(x1,y1,z1,color="black")

        x2,y2,z2 = vec_to_comp(vector)
        ax.scatter(x2,y2,z2,color="blue")
        ax.plot(x2,y2,z2,color="blue")

        x3,y3,z3 = vec_to_comp(rotation(vector,axis,a*np.pi/180))
        ax.scatter(x3,y3,z3,color="green")
        ax.plot(x3,y3,z3,color="green")

        ax.set_xlim3d(-15,15)
        ax.set_ylim3d(-15,15)
        ax.set_zlim3d(-15,15)

        # plt.savefig(f"Images/{a}.png", dpi=300)

        plt.pause(0.0001)
        ax.cla()
        
print( rotation(np.array([5,5,0]),np.array([-1/np.sqrt(2),1/np.sqrt(2),0]),-45*np.pi/180) )
