import matplotlib.pyplot as plt
import numpy as np

with open("reward_history_over_epoch.npy",'rb') as f:
    reward_history = np.load(f)
epochs = 1000
plt.figure()
plt.plot(range(epochs),reward_history[:,0])
plt.plot(range(epochs),reward_history[:,1])
plt.show()