import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from collections import deque

class DQAgent:
    def __init__(self, state_dim, action_dim, lr=0.001, gamma=0.99, epsilon=0.01, max_memory=2000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = lr
        self.gamma = gamma  # Discount factor

        self.epsilon = epsilon  # exploration rate

        self.memory = deque(maxlen=max_memory)  # Experience replay buffer

        self.loss_fn = MeanSquaredError()
        self.optimizer = Adam(learning_rate=self.learning_rate)

    def create_model(self):
        inputs = Input(shape=(self.state_dim,))
        x = Dense(units=64, activation='relu')(inputs)
        x = Dense(units=32, activation='relu')(x)
        x = Dense(units=10, activation='relu')(x)
        out = Dense(units=self.action_dim, activation='linear')(x)
        self.model = Model(inputs=inputs, outputs=out)
        self.model.compile(loss=self.loss_fn, optimizer=self.optimizer, metrics=['accuracy'])

    def choose_action(self, state: np.ndarray):
        # print(len(state.shape))
        if len(state.shape) == 1:
            state = state.reshape(1,state.shape[0])
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, self.action_dim)  # Explore
        q_values = self.model(state)
        return np.argmax(q_values)  # Exploit
    
    def store_transition(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))  # Store in replay buffer

    def update_model(self, batch_size = 10, fit=False):
        if len(self.memory) < batch_size:
            return -1

        batch = np.random.choice(len(self.memory), batch_size, replace=False)

        states, actions, rewards, next_states = zip(*[self.memory[i] for i in batch])
        states = np.array(states)
        actions = np.array(actions)
        rewards = np.array(rewards)
        next_states = np.array(next_states)

        # print("States:",states)
        # print("Actions:",actions)
        # print("Rewards:",rewards)
        # print("next_states:",next_states)

        current_q_value = self.model(states)
        # print("Q_vals:", current_q_value) 

        q_value_t_plus_1 = self.model(next_states)
        # print("t+1 Q_vals:", q_value_t_plus_1)
        
        best_next_action = np.max(q_value_t_plus_1,axis=1) # q_values_t_plus_1 : max Q value

        # print("best actions:", best_next_action)
        target = rewards + self.gamma * best_next_action
        # print("Targets:", target)

        target_one_hot = np.zeros_like(current_q_value)
        for i, action in enumerate(actions):
            target_one_hot[i, action] = target[i]
        
        # print("Targets one hot:", target_one_hot)
        if fit:
            print("Training Model")
            history = self.model.fit(states,target_one_hot, epochs=100, verbose=2)
            print("Training Finished")

            return 0
        else:
            loss_vec = self.train_step(states, target_one_hot)
            loss = tf.reduce_mean(loss_vec)
            return loss
    
    @tf.function
    def train_step(self, x, y):
        with tf.GradientTape() as tape:
            y_pred = self.model(x, training=True)
            loss_value = self.loss_fn(y, y_pred)
        grads = tape.gradient(loss_value, self.model.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_weights))
        return loss_value

if __name__ == '__main__':
    DQ = DQAgent(3, 2)
    DQ.create_model()
    DQ.model.summary()

    example_state = [1,2,3]
    action = 0
    reward = 1
    example_next_state = [0,1,0]

    DQ.store_transition(example_state,1,reward,example_next_state)
    DQ.store_transition(example_state,1,reward,example_next_state)
    DQ.store_transition(example_next_state,1,reward,example_next_state)
    DQ.store_transition(example_state,1,reward,example_next_state)
    DQ.store_transition(example_next_state,1,reward,example_next_state)
    DQ.store_transition(example_state,1,reward,example_next_state)
    DQ.store_transition(example_next_state,1,reward,example_next_state)
    i = 0
    while i < 10000:
        loss = DQ.update_model(5)
        print('Loss:', loss.numpy())
        i+=1