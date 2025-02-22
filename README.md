# README: Q-Learning Pong Implementation

## **What is Q-Learning?**

Q-learning is a model-free reinforcement learning algorithm that allows an agent to learn an optimal policy for decision-making in a given environment. It works by estimating the quality of taking a specific action in a specific state, often represented by a **Q-table**. The Q-values are updated iteratively based on the feedback received from the environment in the form of rewards.

### **Q-Learning Update Equation**
The update equation used to adjust the Q-value is:

Q(s, a) -> Q(s, a) + a * ( r + g * max_{a'} Q(s', a') - Q(s, a) )

Where:
- \( Q(s, a) \): Current Q-value for state \( s \) and action \( a \).
- \( a \): Learning rate, controlling how much new information overrides old estimates.
- \( r \): Reward received after taking action \( a \) in state \( s \).
- \( g \): Discount factor, determining the importance of future rewards.
- \( max_{a'} Q(s', a') \): Maximum Q-value for the next state \( s' \).

This equation ensures the Q-table is updated to improve the agent's future decision-making.

---

## **What is Pong?**

Pong is one of the earliest arcade video games, simulating a table tennis match between two players. Each player controls a paddle that can move vertically to hit a ball. The goal is to prevent the ball from crossing the paddle while trying to score points by getting the ball past the opponent's paddle.

In this implementation, we use two Q-learning agents to control the left and right paddles in a virtual Pong game.

---

## **Code Overview**

The code is structured to simulate a Pong game with the following components:

### 1. **Ball**
The `Ball` class defines the behavior of the ball in the game. Key properties and methods:
- **Position**: `self.x` and `self.y` determine the ball's location.
- **Radius**: `self.r` sets the ball's size.
- **Direction**: `self.dir` is a vector indicating the ball's movement direction.
- **Movement Logic**: The `move` method updates the ball's position, checks for collisions with paddles and walls, and handles scoring events.

### 2. **Paddle**
The `Paddle` class represents a player's paddle. Key properties and methods:
- **Position**: `self.x` and `self.y` set the paddle's location.
- **Length**: Determines how large the paddle is.
- **Movement Logic**: The `move` method ensures the paddle stays within the game boundaries when moving up or down.

### 3. **Board**
The `Board` class manages the game environment. Key features:
- **Game State**: The board is a 2D grid representing the paddles, ball, and empty space.
- **Score Tracking**: Keeps track of the score for both players.
- **Ball Reset**: The `reset_ball` method repositions the ball at the center after a score.
- **Game Update**: The `update` method refreshes the board state by redrawing the paddles and ball.

### 4. **QAgent**
The `QAgent` class implements Q-learning. Key features:
- **Q-Table**: Stores the Q-values for all possible states and actions.
- **Action Selection**: Uses \( epsilon \)-greedy exploration to choose actions (random exploration or exploitation of the Q-table).
- **Q-Value Update**: Implements the Q-learning update equation based on the current state, action, reward, and next state.

---

## **How the Code Works**

### **Game Setup**
1. The `Board` object initializes the environment with a grid of size \( 40 x 40 \).
2. The `Ball` is created with an initial position at the center of the board and a direction vector.
3. Two `Paddle` objects are created for the left and right players, each starting at the middle of their respective sides.

### **Training the Agents**
1. **State Representation**: The state includes paddle positions, ball position, and ball direction, converted to a unique index using the `state_to_index` function.
2. **Action Selection**: Both agents independently choose an action (up, down, or stay) based on the current state.
3. **Environment Interaction**:
   - Actions are applied to move the paddles.
   - The ball moves, and the board state is updated.
4. **Reward Calculation**:
   - Positive rewards are given for actions that lead to advantageous ball angles or scoring.
   - Negative rewards are given for letting the ball pass their paddle.
5. **Q-Table Update**: After observing the reward and next state, each agent updates its Q-values using the Q-learning equation.

### **Visualization**
The game board is displayed using Matplotlib. The paddles and ball are drawn on the grid, and the scores are updated in real time. The visualization allows monitoring of agent performance during training.

---

## **How to Run the Code**
1. Install required libraries:
   ```bash
   pip install matplotlib keyboard numpy
   ```
2. Run the Python script.
3. Observe the training process and gameplay as the agents improve their performance over epochs.

---

## **Future Improvements**
- Implement deep Q-learning with a neural network to handle larger state spaces.
- Introduce randomization in ball direction after scoring to improve agent adaptability.
- Tune hyperparameters (learning rate, discount factor, exploration probability) for better performance.

---

This implementation demonstrates the basics of reinforcement learning through the classic game of Pong. The Q-learning agents learn by trial and error, gradually improving their strategies to win the game.

