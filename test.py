# ------------------------ 1D Heat Equation ------------------------------ #


# import numpy as np
# import matplotlib.pyplot as plt

# def heat_equation_1D(L, nt, nx, alpha, T_left, T_right, T_initial):
#     """
#     Simulates 1D heat equation using Finite Difference Method.

#     Args:
#         L: Length of the rod
#         nt: Number of time steps
#         nx: Number of spatial points
#         alpha: Thermal diffusivity
#         T_left: Temperature at the left boundary
#         T_right: Temperature at the right boundary
#         T_initial: Initial temperature distribution

#     Returns:
#         Temperature distribution at each time step
#     """

#     dx = L / (nx - 1)
#     dt = 2.1 * dx**2   # Stability condition

#     x = np.linspace(0, L, nx)
#     T = T_initial.copy()
#     T_history = [T.copy()]

#     for n in range(nt):
#         T_new = T.copy()
#         for i in range(1, nx - 1):
#             T_new[i] = T[i] + alpha * dt / dx**2 * (T[i+1] - 2*T[i] + T[i-1])
#         T_new[0] = T_left
#         T_new[-1] = T_right
#         T = T_new.copy()
#         T_history.append(T.copy())

#     return T_history, x

# # Parameters
# L = 1.0  # Length of the rod
# nt = 1000  # Number of time steps
# nx = 101  # Number of spatial points
# alpha = 0.001  # Thermal diffusivity
# T_left = 100.0  # Temperature at the left boundary
# T_right = 0.0  # Temperature at the right boundary
# T_initial = 20.0 * np.ones(nx)  # Initial temperature distribution

# # Simulate
# T_history, x = heat_equation_1D(L, nt, nx, alpha, T_left, T_right, T_initial)

# # Visualize
# plt.ion()  # Interactive mode
# fig, ax = plt.subplots()
# line, = ax.plot(x, T_history[0])
# ax.set_xlabel('Position (m)')
# ax.set_ylabel('Temperature (C)')
# ax.set_ylim([0, 120])

# for T in T_history:
#     line.set_ydata(T)
#     fig.canvas.draw()
#     plt.pause(0.01)

# plt.ioff()
# plt.show()

# ------------------------ 2D Heat Equation ------------------------------ #

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# def heat_equation_2D(L, nt, nx, ny, alpha, T_boundary, T_initial):
#     """
#     Simulates 2D heat equation using Finite Difference Method.

#     Args:
#         L: Length of the square domain
#         nt: Number of time steps
#         nx: Number of spatial points in x-direction
#         ny: Number of spatial points in y-direction
#         alpha: Thermal diffusivity
#         T_boundary: Boundary temperature
#         T_initial: Initial temperature distribution

#     Returns:
#         Temperature distribution at each time step
#     """

#     dx = L / (nx - 1)
#     dy = L / (ny - 1)
#     dt = 0.1 * min(dx**2, dy**2) / (2*alpha)  # Stability condition

#     x = np.linspace(0, L, nx)
#     y = np.linspace(0, L, ny)
#     X, Y = np.meshgrid(x, y)

#     T = T_initial.copy()
#     T_history = [T.copy()]

#     for n in range(nt):
#         T_new = T.copy()
#         for i in range(1, nx-1):
#             for j in range(1, ny-1):
#                 T_new[i, j] = T[i, j] + alpha * dt / (dx**2) * (T[i+1, j] - 2*T[i, j] + T[i-1, j]) + alpha * dt / (dy**2) * (T[i, j+1] - 2*T[i, j] + T[i, j-1])
        
#         # Apply boundary conditions
#         T_new[0, :] = T_boundary
#         T_new[-1, :] = T_boundary
#         T_new[:, 0] = T_boundary
#         T_new[:, -1] = T_boundary
#         T = T_new.copy()
#         T_history.append(T.copy())

#     return T_history, X, Y

# # Parameters
# L = 1.0  # Length of the square domain
# nt = 1000  # Number of time steps
# nx = 50  # Number of spatial points in x-direction
# ny = 50  # Number of spatial points in y-direction
# alpha = 0.001  # Thermal diffusivity
# T_boundary = 100.0  # Boundary temperature
# T_initial = 20.0 * np.ones((nx, ny))  # Initial temperature distribution

# # Simulate
# T_history, X, Y = heat_equation_2D(L, nt, nx, ny, alpha, T_boundary, T_initial)

# # Visualize
# fig, ax = plt.subplots()
# im = ax.imshow(T_history[0], cmap='hot', interpolation='nearest',vmin=T_initial.min(), vmax=T_boundary)
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_title('Temperature Distribution')

# def update_plot(frame):
#     im.set_array(T_history[frame])
#     return im,

# ani = FuncAnimation(fig, update_plot, frames=len(T_history), interval=20)
# plt.show()

# ------------------------ 1D Heat Equation Dataset Generator ------------------------------ #
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
def generate_heat_equation_data(L, nt, nx, alpha, T_left, T_right, T_initial)->np.ndarray:
    """
    Generates a dataset for a 1D heat equation.

    Args:
        L: Length of the rod
        nt: Number of time steps
        nx: Number of spatial points
        alpha: Thermal diffusivity
        T_left: Temperature at the left boundary
        T_right: Temperature at the right boundary
        T_initial: Initial temperature distribution

    Returns:
        A tuple of input features and output temperatures.
    """

    dx = L / (nx - 1)
    dt = dx/100  # Stability condition

    T = T_initial.copy()
    T_history = [T.copy()]

    for n in range(nt):
        T_new = T.copy()
        for i in range(1, nx - 1):
            T_new[i] = T[i] + alpha * dt / dx**2 * (T[i+1] - 2*T[i] + T[i-1])
        T_new[0] = T_left
        T_new[-1] = T_right
        T = T_new.copy()        
        T_history.append(T)

    return np.array(T_history)

def add_noise(data,noise_mag)->np.ndarray:
    noise = noise_mag*np.random.random(data.shape)-noise_mag/2
    outliers = np.zeros_like(noise)
    x = np.random.randint(0,noise.shape[1], size=10)
    if noise_mag != 0:
        Ou = np.random.randint(5,10,size=5)
        Ol = np.random.randint(-10,5,size=5)
        O = np.hstack((Ou,Ol))
        outliers[:,x] = O
    data += noise + outliers
    return data

def set_T_init(L,size=100):
    x = np.linspace(0, L, size)
    while True:
        T_init = np.array([np.sin(w*x) for w in np.random.randint(15,50,size=np.random.randint(5,20))]).sum(axis=0)
        T_min = np.min(T_init)
        T_max = np.max(T_init)
        T_init = 100 * (T_init - T_min) / (T_max - T_min)

        yield T_init

def create_dataset(trial_count, readings_per_trial,nx,nt,alpha,noise_mag,path):
    for trial_no in range(trial_count):
        data = []
        for _ in range(readings_per_trial):
            L = np.round(np.random.random()+0.2,2)
            generator_T_init = set_T_init(L,nx)

            T_init = next(generator_T_init)
            T_right = T_init[-1]
            T_left = T_init[0]
            T_history = generate_heat_equation_data(L,nt,nx,alpha,T_left,T_right,T_init)
            T_history_noise = add_noise(T_history.copy(),noise_mag)
            data_values = [L, nx] + T_history_noise.flatten().tolist()
            data.append(data_values)
        print(trial_no)
        dataset = pd.DataFrame(columns=["L","nx"] + [f"val_{i}" for i in range(nx*(nt+1))], data=data).round(2)
        if 'test' in path:
            dataset['Usage'] = ["Private" if i%2 == 0 else "Public" for i in range(len(dataset))]
            dataset.to_csv(f"submission_{trial_no}.csv",index_label="ID")
            dataset.drop("Usage",axis=1,inplace=True)
            dataset[[f"val_{i}" for i in range(nx,nx*(nt+1))]] = np.zeros((nt*nx))
        dataset.to_csv(f"{path}/dataset_{trial_no}.csv",index_label="ID")

create_dataset(25,100,50,50,0.14159,5,'dataset/train')
create_dataset(10,100,50,50,0.14159,4,'dataset/valid')
create_dataset(1,100,50,50,0.14159,0,'dataset/test')