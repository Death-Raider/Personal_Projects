import numpy as np
from PIL import Image

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

def process_img(file,axis,angle,save):
    img = Image.open(file)
    pixels = img.load()
    size = img.size
    new_img = Image.new(mode="RGB",size=size)
    new_pixels = new_img.load()
    duplicate = dict()
    for x in range(size[0]):
        for y in range(size[1]):
            pix = pixels[x,y][:3]
            if f"{pix}" in duplicate:
                new_pixels[x,y] = duplicate[f"{pix}"]
            else:
                vector = np.array(pix)-127
                new = rotation(vector,axis,angle)+127
                new_pixels[x,y] = ( int(new[0]), int(new[1]), int(new[2]) )
                duplicate[f"{pix}"] = new_pixels[x,y]
    new_img.save(f"{save}.png")
    new_img.close()
    img.close()

axis = np.array([1,0,0])
axis = axis/np.linalg.norm(axis)
file = "color.jpg"

for angle in range(360):
    save = f"Images/{angle}"
    angle_rad = angle*np.pi/180
    process_img(file,axis,angle_rad,save)
    print(angle)
