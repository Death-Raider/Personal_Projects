import numpy as np

class QAgent:
    def __init__(self, n_states, n_actions, learning_rate=0.8, discount_factor=0.95, exploration_prob=0.2):
        self.q_table = np.zeros((n_states, n_actions), dtype=np.float16)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_prob = exploration_prob

    def choose_action(self, state):
        if np.random.rand() < self.exploration_prob:
            return np.random.randint(0, self.q_table.shape[1])  # Explore
        return np.argmax(self.q_table[state])  # Exploit

    def update_q_value(self, state, action, reward, next_state):
        best_next_action = np.max(self.q_table[next_state])
        self.q_table[state, action] += self.learning_rate * (
            reward + self.discount_factor * best_next_action - self.q_table[state, action]
        )

    def save_q_table(self, file_path):
        np.save(file_path, self.q_table)

    def load_q_table(self, file_path):
        self.q_table = np.load(file_path)