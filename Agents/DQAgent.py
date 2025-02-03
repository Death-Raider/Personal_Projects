import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from collections import deque

class DeepQNetwork():
    def __init__(self, state_dim, action_dim, hidden_layers=[64, 64]):
        inp = Input(shape=(state_dim,))
        x = Dense(hidden_layers[0], activation='relu')(inp)
        for units in hidden_layers[1:]:
            x = Dense(units, activation='relu')(x)
        out = Dense(action_dim, activation='linear')(x)  # Q-values for each action
        self.model = Model(inputs=inp, outputs=out)
        # self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    def call(self, state):
        return self.model(state)

class DQAgent:
    def __init__(self, state_dim, action_dim, lr=0.001, gamma=0.99, max_memory=2000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma  # Discount factor
        self.epsilon = 1.0  # Initial exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.memory = deque(maxlen=max_memory)  # Experience replay buffer

        # Q-Network
        self.q_network = DeepQNetwork(state_dim, action_dim, hidden_layers=[32,64])
        self.optimizer = Adam(learning_rate=lr)
        self.q_network.model.compile(optimizer=Adam(learning_rate=lr), loss='mse')

    def remember(self, state, action, reward, next_state, done):
        """Stores experience in replay memory."""
        self.memory.append((state, action, reward, next_state, done))

    def get_action(self, state):
        """Epsilon-Greedy Policy."""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_dim)  # Explore
        q_values = self.q_network.model.predict(np.array([state]), verbose=0)
        return np.argmax(q_values[0])  # Exploit
   
    # @tf.function
    def train_step(self, batch_size=32):
        """Trains the model using experience replay."""

        batch = self.memory  # Train on all memory (assuming small dataset)
        for state, action, reward, next_state, done in batch:
            tf.print(state, action, reward, next_state, done)
            state = np.array([state], dtype=np.float32)
            next_state = np.array([next_state], dtype=np.float32)

            with tf.GradientTape() as tape:
                q_values = self.q_network.model.predict(state)  # Forward pass
                next_q_values = self.q_network.model.predict(next_state)  

                target_q_values = tf.identity(q_values)  # Clone to avoid modifying original
                if done:
                    target_q_values = reward
                else:
                    target_q_values = reward + self.gamma * tf.reduce_max(next_q_values)

                # Compute loss
                tf.print(target_q_values)
                tf.print(q_values)
                loss = tf.square(target_q_values, q_values[0, action])
            tf.print("Loss:",loss.numpy())  # Print the loss

            # Compute gradients and update weights
            gradients = tape.gradient(loss, self.q_network.model.trainable_variables)
            self.optimizer.apply_gradients(zip(gradients, self.q_network.model.trainable_variables))

        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
# Example usage
if __name__ == "__main__":
    agent = DQAgent(state_dim=4, action_dim=2)

    # Fake experience for testing
    state = np.array([0.1, 0.2, 0.3, 0.4])
    next_state = np.array([0.5, 0.6, 0.7, 0.8])
    action = 1
    reward = 10
    done = False

    # Store experience and train
    print("Selected action:", agent.get_action(state))
    agent.remember(state, action, reward, next_state, done)
    agent.train_step(batch_size=1)

    # Get an action using epsilon-greedy
    print("Selected action:", agent.get_action(state))
