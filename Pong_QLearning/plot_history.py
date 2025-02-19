import matplotlib.pyplot as plt
import numpy as np

with open("Pong_QLearning/data/reward_history_over_epoch.npy",'rb') as f:
    reward_history = np.load(f)

epochs = len(reward_history)

print(reward_history)

plt.figure()
plt.plot(range(epochs),reward_history[:,0]) # reward 1
plt.show()
plt.figure()
plt.plot(range(epochs),reward_history[:,1]) # reward 2
plt.show()
plt.figure()
plt.plot(range(epochs),reward_history[:,2]) # loss 1
plt.show()
plt.figure()
plt.plot(range(epochs),reward_history[:,3]) # loss 2
plt.show()

plt.figure()
plt.plot(range(epochs),reward_history[:,0])
plt.plot(range(epochs),reward_history[:,1])
plt.show()

plt.figure()
plt.plot(range(epochs),reward_history[:,2])
plt.plot(range(epochs),reward_history[:,3])
plt.show()