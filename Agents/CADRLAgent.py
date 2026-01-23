import numpy as np
import tensorflow as tf
from Agents.DQAgent import DQAgent

class CADRLStyleAgent(DQAgent):
    """
    Uses DQN architecture but CADRL action selection logic:
    - Sample multiple actions
    - Simulate next state for each
    - Evaluate with value network
    - Choose action with best worst-case value (conservative)
    """
    
    def __init__(self, state_dim, action_dim, **kwargs):
        super().__init__(state_dim, action_dim, **kwargs)
        
        # CADRL-specific parameters
        self.num_action_samples = kwargs.get('num_action_samples', 8)  # Sample all 8 directions
        self.conservative = kwargs.get('conservative', True)  # Use min (conservative) vs mean
        self.time_step = kwargs.get('time_step', 1.0)
        
    def choose_action(self, state, robot=None, goal=None, other_robots=None):
        """
        CADRL-style action selection with lookahead
        
        Args:
            state: Current state observation (same as DQN)
            robot: Optional robot object for simulation
            goal: Optional goal object
            other_robots: Optional list of other robots in view
        
        Returns:
            action: Best action index (0-7)
        """
        # Epsilon-greedy exploration (same as DQN)
        if np.random.rand() <= self.epsilon:
            return np.random.randint(self.action_dim)
        
        # If we don't have robot info, fall back to DQN
        if robot is None or goal is None:
            return super().choose_action(state)
        
        # CADRL logic: evaluate all actions with lookahead
        action_values = []
        
        for action in range(self.action_dim):
            # Simulate taking this action
            simulated_next_states = self._simulate_action(
                state, action, robot, goal, other_robots
            )
            
            # Evaluate all possible next states (for each nearby robot)
            if len(simulated_next_states) > 0:
                # Get Q-values for all next states
                next_states_batch = np.array(simulated_next_states, dtype=np.float32)
                q_values = self.model(next_states_batch, training=False)
                
                # Take max Q-value for each next state (best action in next state)
                max_q_values = tf.reduce_max(q_values, axis=1)
                
                # Conservative: take MINIMUM over all possible next states
                # (worst case if other robots move unpredictably)
                if self.conservative:
                    action_value = tf.reduce_min(max_q_values).numpy()
                else:
                    action_value = tf.reduce_mean(max_q_values).numpy()
            else:
                # No other robots, just evaluate this action normally
                next_state = self._simple_propagate(state, action, robot, goal)
                q_values = self.model(np.array([next_state]), training=False)
                action_value = tf.reduce_max(q_values[0]).numpy()
            
            action_values.append(action_value)
        
        # Return action with best value
        return np.argmax(action_values)
    
    def _simulate_action(self, state, action, robot, goal, other_robots):
        """
        Simulate taking an action and generate possible next states
        
        Returns:
            List of possible next states (one per nearby robot configuration)
        """
        simulated_states = []
        
        # Simulate robot's movement
        next_robot_pos = self._propagate_robot(robot, action)
        
        # For each nearby robot, simulate their possible movements
        if other_robots and len(other_robots) > 0:
            for other_robot in other_robots[:3]:  # Limit to 3 nearest (performance)
                # Assume other robot continues current direction (simple model)
                # Or sample possible directions
                for other_action in range(self.action_dim):
                    next_other_pos = self._propagate_robot(other_robot, other_action)
                    
                    # Generate state representation for this configuration
                    next_state = self._construct_state(
                        next_robot_pos, goal, other_robot, next_other_pos
                    )
                    simulated_states.append(next_state)
        else:
            # No other robots, just propagate self
            next_state = self._simple_propagate(state, action, robot, goal)
            simulated_states.append(next_state)
        
        return simulated_states
    
    def _propagate_robot(self, robot, action):
        """
        Simulate robot taking an action for one timestep
        
        Returns:
            (x, y, direction) tuple
        """
        # Direction mappings: [NE, N, NW, W, E, SW, S, SE]
        row_order = [-1, -1, -1,  0, 0,  1, 1, 1]
        col_order = [-1,  0,  1, -1, 1, -1, 0, 1]
        
        new_x = robot.x + robot.v * col_order[action] * self.time_step
        new_y = robot.y + robot.v * row_order[action] * self.time_step
        new_dir = action
        
        return (new_x, new_y, new_dir)
    
    def _construct_state(self, robot_pos, goal, other_robot, other_pos):
        """
        Construct state representation from positions
        
        This should match your robot.get_DQL_state() format
        """
        # Simplified - you'll need to match your exact state format
        rx, ry, rdir = robot_pos
        ox, oy, odir = other_pos
        
        # Calculate relative positions
        dist_to_goal = np.hypot(goal.x - rx, goal.y - ry)
        angle_to_goal = np.arctan2(goal.y - ry, goal.x - rx)
        
        dist_to_other = np.hypot(ox - rx, oy - ry)
        angle_to_other = np.arctan2(oy - ry, ox - rx)
        
        # Build state (simplified - match your actual format)
        # Your actual state: (21x21x2) + 2 = 884 features
        # Here we create a simplified version
        state = np.zeros(self.state_dim)
        
        # Global features (last 2 elements)
        state[-2] = goal.x - rx  # goal_dx
        state[-1] = goal.y - ry  # goal_dy
        
        # Local view features (simplified)
        # In reality, you'd need to reconstruct the full view grid
        # For now, encode the nearby robot position
        view_size = 21
        center = view_size // 2
        
        # Map other robot to grid position
        rel_x = int((ox - rx) + center)
        rel_y = int((oy - ry) + center)
        
        if 0 <= rel_x < view_size and 0 <= rel_y < view_size:
            idx = rel_y * view_size + rel_x
            state[idx * 2] = dist_to_other  # Distance feature
            state[idx * 2 + 1] = angle_to_other  # Angle feature
        
        return state
    
    def _simple_propagate(self, state, action, robot, goal):
        """
        Simple propagation without considering other robots
        """
        next_pos = self._propagate_robot(robot, action)
        # Return modified state with updated goal distance
        next_state = state.copy()
        rx, ry, _ = next_pos
        next_state[-2] = goal.x - rx
        next_state[-1] = goal.y - ry
        return next_state