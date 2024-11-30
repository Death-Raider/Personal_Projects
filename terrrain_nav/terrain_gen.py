import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from astar import *

def gen_peak(z, peak_height, peak_width, peak_x, peak_y):

    # Ensure peak_x and peak_y are within the terrain bounds
    peak_x = max(0, min(z.shape[0] - 1, peak_x))
    peak_y = max(0, min(z.shape[1] - 1, peak_y))

    # Calculate the distance from each point to the peak center
    dx, dy = np.meshgrid(np.arange(z.shape[0]), np.arange(z.shape[1]))
    distance = np.sqrt((dx - peak_x)**2 + (dy - peak_y)**2)

    # Apply a Gaussian function to create a smooth peak shape
    peak_shape = peak_height * np.exp(-distance**2 / (2 * peak_width**2))

    return peak_shape

def generate_lidar_data(x_range, y_range, resolution=0.2):
    # Define dimensions of the terrain (adjust as needed)
    x_min, x_max = x_range
    y_min, y_max = y_range

    # Create a grid of points
    x, y = np.meshgrid(np.arange(x_min, x_max + resolution, resolution),
                    np.arange(y_min, y_max + resolution, resolution))
    # Generate terrain heights with noise
    z = np.zeros_like(x) # Adjust height range as needed
    lidar_data = np.dstack((x, y, z))
    return lidar_data

def create_cost_map_from_terrain(terrain):
  return terrain[:,:,2]


RESOLUTION = 1.0
WIDTH = 100
HEIGHT = 100
peaks = [
    {
        "x":np.random.randint(0,WIDTH)/RESOLUTION,
        "y":np.random.randint(0,HEIGHT)/RESOLUTION,
        "height": np.random.randint(1,2)/(RESOLUTION*10),
        "width":np.random.randint(5,10)/RESOLUTION
    }
    for _ in range(10)
]
lidar_data = generate_lidar_data(
    x_range = (0,WIDTH), 
    y_range = (0,HEIGHT), 
    resolution = RESOLUTION
)
for peak in peaks:
    peak = gen_peak(
        z = lidar_data[:,:,2], 
        peak_height = peak['height'], 
        peak_width = peak['width'], 
        peak_x = peak['x'],  
        peak_y = peak['y']
    )
    lidar_data[:,:,2] += peak

point_inits = [
    [1,1], # start
    [ int(WIDTH/RESOLUTION)-1 , int(HEIGHT/RESOLUTION)-1 ] # end
]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(lidar_data[:,:,0],lidar_data[:,:,1],lidar_data[:,:,2], cmap='terrain',alpha = 0.5)

for i in range(2):
    x,y,z = lidar_data[point_inits[i][1],point_inits[i][0]]
    ax.scatter3D(x,y,z)
    point_inits[i].append(z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('Generated Terrain')
plt.show()

graph = create_cost_map_from_terrain(lidar_data)
path = a_star_search(graph, point_inits[0], point_inits[1])
print(graph)
print(path)
cost_map = lidar_data[:,:,2]
if path != None:
   for p in path:
      cost_map[p[1]][p[0]] = 0.1
plt.figure()
plt.imshow(cost_map)
plt.show()