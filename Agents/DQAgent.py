import numpy as np
import random
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input, BatchNormalization, Dropout
from tensorflow.keras.optimizers import Adam
import keras

class DQAgent:
    def __init__(self, state_dim, action_dim, lr=0.001, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, memory_size=2000, batch_size=32, target_update_freq=100):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.memory = deque(maxlen=memory_size)
        self.steps = 0

        # Initialize networks and optimizer
        self.model = self.build_model()
        self.target_model = self.build_model()
        self.optimizer = Adam(learning_rate=self.lr)
        self.update_target_network()

    def build_model(self):
        inputs = Input(shape=(self.state_dim,))
        x = Dense(128, activation='relu')(inputs)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)
        x = Dense(32, activation='relu')(x)
        outputs = Dense(self.action_dim, activation='linear')(x)
        return Model(inputs=inputs, outputs=outputs)
    
    def save_model(self,directory):
        if directory[-1] == '/':
            directory = directory[:-1]
        self.target_model.save(directory+"/target_model.keras")
        self.model.save(directory+"/model.keras")
    
    def load_model(self, directory):
        if directory[-1] == '/':
            directory = directory[:-1]
        self.target_model = keras.saving.load_model(directory+"/target_model.keras")
        self.model = keras.saving.load_model(directory+"/model.keras")

    def update_target_network(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.randint(self.action_dim)
        state = np.array(state).reshape(1, -1)
        q_values = self.model(state, training=False)
        return np.argmax(q_values[0])

    def replay(self, batch_size):
        if batch_size == None:
            batch_size = self.batch_size
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([t[0] for t in minibatch], dtype=np.float32)
        actions = np.array([t[1] for t in minibatch], dtype=np.int32)
        rewards = np.array([t[2] for t in minibatch], dtype=np.float32)
        next_states = np.array([t[3] for t in minibatch], dtype=np.float32)
        dones = np.array([t[4] for t in minibatch], dtype=np.float32)

        states_tensor = tf.convert_to_tensor(states)
        next_states_tensor = tf.convert_to_tensor(next_states)
        rewards_tensor = tf.convert_to_tensor(rewards)
        actions_tensor = tf.convert_to_tensor(actions)
        dones_tensor = tf.convert_to_tensor(dones)

        loss = self.train_step(states_tensor, actions_tensor, rewards_tensor, next_states_tensor, dones_tensor)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.update_target_network()
        
        return loss

    @tf.function
    def train_step(self, states, actions, rewards, next_states, dones):
        with tf.GradientTape() as tape:
            next_q = self.target_model(next_states, training=False)
            max_next_q = tf.reduce_max(next_q, axis=1)
            target_q = rewards + self.gamma * max_next_q * (1 - dones)

            current_q = self.model(states, training=True)
            action_mask = tf.one_hot(actions, self.action_dim)
            current_action_q = tf.reduce_sum(current_q * action_mask, axis=1)
            error = tf.subtract(target_q, current_action_q)
            loss = tf.reduce_mean(tf.where(tf.abs(error) < 1.0, 0.5 * tf.square(error), tf.abs(error) - 0.5))

        gradients = tape.gradient(loss, self.model.trainable_variables)
        gradients, _ = tf.clip_by_global_norm(gradients, 5.0)  # Clip gradients
        self.optimizer.apply_gradients(
            zip(gradients, self.model.trainable_variables)
        )
        return loss
