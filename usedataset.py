import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv("dataset/train/dataset_0.csv")
print(data)
print(data.describe())

certain_data = data.iloc[13]
print(certain_data)
ID = int(certain_data['ID'])
L = float(certain_data['L'])
nx = int(certain_data['nx'])
temp_vals = certain_data.values[3:].reshape((-1,nx))
print(temp_vals.shape)

plt.ion()
x = np.linspace(0,L,nx)
fig, ax = plt.subplots()
line, = ax.plot(x, temp_vals[0])
ax.set_xlabel('Position (m)')
ax.set_ylabel('Temperature (C)')
ax.set_ylim([0, 120])

for T in temp_vals:
    line.set_ydata(T)
    fig.canvas.draw()
    plt.pause(0.01)

plt.ioff()
plt.show()