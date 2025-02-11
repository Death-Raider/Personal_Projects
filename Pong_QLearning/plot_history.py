import matplotlib.pyplot as plt
import numpy as np

with open("reward_history_over_epoch.npy",'rb') as f:
    reward_history = np.load(f)

# with open("dataset.npy",'rb') as f:
#     dataset = np.load(f,allow_pickle=True)

epochs = len(reward_history)

print(reward_history)
# print(dataset)

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