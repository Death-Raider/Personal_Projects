import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input, BatchNormalization, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError, Huber
from collections import deque

class DQAgent:
    def __init__(self, state_dim, action_dim, lr=0.001, gamma=0.99, epsilon=0.01, max_memory=2000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = lr
        self.gamma = gamma  # Discount factor

        self.epsilon = epsilon  # exploration rate

        self.memory = deque(maxlen=max_memory)  # Experience replay buffer

        self.loss_fn = Huber()
        self.optimizer = Adam(learning_rate=self.learning_rate)

    def create_model(self):
        inputs = Input(shape=(self.state_dim,))
        inputs_BN = BatchNormalization()(inputs)
        x = Dense(units=256, activation='relu')(inputs_BN)
        x = Dropout(0.4)(x)
        x = Dense(units=128, activation='relu')(x)
        x = Dropout(0.4)(x)
        x = BatchNormalization()(x)
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
        X,y = self.get_train_data_from_state_vector(states, actions, rewards, next_states)
        # print(y)
        if fit:
            history = self.model.fit(X,y, epochs=10, batch_size=batch_size, verbose=0)
            return 0
        else:
            loss_vec = self.train_step(X, y)
            loss = tf.reduce_mean(loss_vec)
            return loss
    
    def get_train_data_from_state_vector(self,states, actions, rewards, next_states):
        # print("Q_vals:", current_q_value) 
        current_q_value = self.model(states)
        # print("t+1 Q_vals:", q_value_t_plus_1)
        q_value_t_plus_1 = self.model(next_states)
        # q_values_t_plus_1 -> max Q value
        best_next_action = np.max(q_value_t_plus_1,axis=1)
        target = rewards + self.gamma * best_next_action
        target_one_hot = np.zeros_like(current_q_value)
        for i, action in enumerate(actions):
            target_one_hot[i, action] = target[i]
        return states, target_one_hot

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