import numpy as np

A = np.arange(-1,1,0.5)
B = np.arange(-1,1,0.5)
A,B = np.meshgrid(A,B)
Z = 5*np.ones_like(A)
W = 10*np.ones_like(A)

print("A:",A,A.shape)
print("B:",B,B.shape)
print("Z:",Z,Z.shape)
print("W:",W,W.shape)

Vec = np.array([[A+B*1j, Z+W*1j]])

print("Vec:", Vec, Vec.shape)

complex_matrix = np.array([
    [np.ones_like(A), 2*np.ones_like(A)],
    [np.zeros_like(A), np.ones_like(A)]
],dtype="complex")

# print("complex matrix:", complex_matrix, complex_matrix.shape)

R = np.einsum('ij...,kj...->i...', complex_matrix,Vec, optimize = True)

print("R:" , R, R.shape)