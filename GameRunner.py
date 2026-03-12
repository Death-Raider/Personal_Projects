# core/game_runner.py
"""
GameRunner: Universal training loop using dependency injection
Works with any BaseEnvironment implementation
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Callable, Optional, Any
from tqdm import tqdm
from Environments.baseenvironment import BaseEnvironment
import time

class GameRunner:
    """
    Universal game runner that works with any BaseEnvironment.
    All environment-specific logic is delegated to the environment class.
    
    This keeps GameRunner clean and environment-agnostic.
    """
    
    def __init__(self, environment: BaseEnvironment):
        """
        Initialize GameRunner with an environment
        
        Args:
            environment: Instance of BaseEnvironment (Pong, GoalChasing, etc.)
        """
        self.env = environment
        self.metrics = {
            'rewards': [],
            'losses': [],
            'episode_lengths': [],
            'custom_metrics': {}
        }
    
    def run(self,
            epochs: int = 100,
            max_steps_per_episode: int = 1000,
            reward_functions: Optional[Dict[str, Callable]] = None,
            termination_condition: Optional[Callable] = None,
            step_callback: Optional[Callable] = None,
            episode_callback: Optional[Callable] = None,
            render: bool = False,
            render_last_epoch: bool = False,
            save_metrics: bool = False,
            save_models: bool = False,
            save_model_freq: int = 1,
            save_directory: str = './saved_models',
            verbose: int = 1,
            train: bool = True,
            action_override: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Run training loop
        
        Args:
            epochs: Number of training epochs
            max_steps_per_episode: Maximum steps before forced termination
            reward_functions: Optional custom reward functions per agent
                             If None, uses environment's default
            termination_condition: Optional custom termination condition
                                  If None, uses environment's default
            step_callback: Called every step
            episode_callback: Called after each epoch
            render: Render every step
            render_last_epoch: Only render final epoch
            save_metrics: Save training metrics
            save_models: Save agent models
            save_directory: Directory for saving
            verbose: Verbosity level (0=silent, 1=progress bars, 2=detailed)
        
        Returns:
            Dictionary of collected metrics
        """
        
        # Use environment defaults if not provided
        if reward_functions is None:
            default_reward = self.env.get_default_reward_function()
            reward_functions = {name: default_reward for name in self.env.agents.keys()}
        
        if termination_condition is None:
            termination_condition = self.env.get_default_termination_condition()
        
        if render or render_last_epoch:
            self.env.render_init()
        # Training loop
        for epoch in tqdm(range(epochs), desc="Training Progress", disable=(verbose < 1)):
            self.env.current_epoch = epoch
            
            # Reset environment
            self.env.reset_episode()
            
            # Metrics for this epoch
            epoch_rewards = {name: [] for name in self.env.agents.keys()}
            epoch_losses = {name: [] for name in self.env.agents.keys()}
            step = 0
            
            # Render control
            should_render = render or (render_last_epoch and epoch == epochs - 1)
            
            # Episode loop
            pbar = tqdm(total=max_steps_per_episode, desc=f"    Episode Loop: Epoch {epoch+1}/{epochs}", disable=(verbose < 2), leave=False)
            while True:
                if termination_condition(self.env.board, step) or step >= max_steps_per_episode:
                    break
                # Get states from environment
                states = self.env.get_states()

                # Agents choose actions
                actions = {}
                for name, agent in self.env.agents.items():
                    if name in states:
                        if action_override and name in action_override:
                            actions[name] = action_override[name](states[name])
                        else:
                            actions[name] = agent.choose_action(states[name])

                # Execute actions in environment
                self.env.execute_actions(actions)

                # Get new states
                next_states = self.env.get_states()
                
                # Compute rewards using provided functions
                rewards = {}
                for name in self.env.agents.keys():
                    if name in reward_functions and name in states:
                        rewards[name] = reward_functions[name](
                            self.env.board, name,
                            states=states,
                            actions=actions,
                            next_states=next_states,
                            step=step
                        )
                    else:
                        rewards[name] = 0.0

                # Check if done
                dones = self.env.check_done(step)

                # Update agents
                losses = {}
                if train:
                    s1 = time.time()
                    for name, agent in self.env.agents.items():
                        if name not in states or name not in next_states:
                            continue
                        # Store experience for replay-based agents
                        if hasattr(agent, 'remember'):
                            agent.remember(
                                states[name],
                                actions[name],
                                rewards[name],
                                next_states[name],
                                dones[name]
                            )
                        # Different update methods for different agent types
                        
                        if hasattr(agent, 'replay'):
                            # DQN-style agents
                            loss = agent.replay(None)
                            losses[name] = loss if loss is not None else 0.0
                            
                        elif hasattr(agent, 'update_q_value'):
                            # Q-Learning agents
                            try:
                                agent.update_q_value(
                                    states[name],
                                    actions.get(name, 0),
                                    rewards.get(name, 0),
                                    next_states[name]
                                )
                            except:
                                pass  # Handle index errors gracefully
                            losses[name] = 0.0
                    # print("First Half: ",time.time()-s1)

                # Record step metrics
                for name in self.env.agents.keys():
                    if name in rewards:
                        epoch_rewards[name].append(rewards[name])
                    if name in losses:
                        epoch_losses[name].append(losses[name])
                
                # Step callback
                if step_callback:
                    step_callback(self.env.board, self.env.agents, step, epoch, self)

                # Render
                if should_render:
                    self.env.render()
                
                step += 1
                pbar.update(1)
            pbar.close()
            
            # Record epoch metrics
            self.metrics['rewards'].append({
                name: float(np.mean(rewards_list)) if rewards_list else 0
                for name, rewards_list in epoch_rewards.items()
            })
            self.metrics['losses'].append({
                name: float(np.mean(losses_list)) if losses_list else 0
                for name, losses_list in epoch_losses.items()
            })
            self.metrics['episode_lengths'].append(step)
            
            # Episode callback
            if episode_callback:
                episode_callback(self.env.board, self.env.agents, epoch, self.metrics, self)
            
            # Verbose logging
            if verbose >= 2:
                self._log_epoch(epoch, epoch_rewards, epoch_losses, step)
            
            # Save models periodically
            if save_models and (epoch + 1) % save_model_freq == 0:
                self._save_models(save_directory, epoch)
        
        # Final save
        if save_metrics:
            self._save_metrics(save_directory)
        
        if save_models:
            self._save_models(save_directory, 'final')
        
        return self.metrics
    
    # ============ Utility Methods ============
    
    def _log_epoch(self, epoch, rewards, losses, steps):
        """Log epoch information"""
        avg_rewards = {name: np.mean(r) if r else 0 for name, r in rewards.items()}
        avg_losses = {name: np.mean(l) if l else 0 for name, l in losses.items()}
        print(f"Epoch {epoch}: Steps={steps}, Rewards={avg_rewards}, Losses={avg_losses}")
    
    def _save_models(self, directory, epoch):
        """Save all agent models"""
        import os
        os.makedirs(directory, exist_ok=True)
        for name, agent in self.env.agents.items():
            if hasattr(agent, 'save_model'):
                os.makedirs(f"{directory}/{name}_epoch_{epoch}", exist_ok=True)
                agent.save_model(f"{directory}/{name}_epoch_{epoch}")
    
    def _save_metrics(self, directory):
        """Save training metrics"""
        import os
        import json
        os.makedirs(directory, exist_ok=True)
        
        serializable_metrics = {
            'rewards': self.metrics['rewards'],
            'episode_lengths': self.metrics['episode_lengths'],
            'losses': self.metrics['losses']
        }
        
        with open(f"{directory}/metrics.json", 'w') as f:
            json.dump(serializable_metrics, f, indent=2)
        with open(f"{directory}/custom_metrics.json", 'w') as f:
            json.dump(self.metrics['custom_metrics'], f, indent=2)