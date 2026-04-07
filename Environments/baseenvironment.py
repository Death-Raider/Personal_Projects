# core/base_environment.py
"""
Base class for all MARL environments
Each environment implements its own state management, action execution, and defaults
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Tuple, List
import numpy as np
import matplotlib.pyplot as plt



class BaseEnvironment(ABC):
    """
    Abstract base class for MARL environments.
    Each environment handles its own:
    - State representation
    - Action execution
    - Default reward functions
    - Termination conditions
    - Rendering
    
    The GameRunner just orchestrates these components.
    """
    
    def __init__(self, board, agents: Dict[str, Any]):
        """
        Initialize environment wrapper
        
        Args:
            board: The actual game board instance
            agents: Dictionary of agent instances
        """
        self.board = board
        self.agents = agents
        self.current_step = 0
        self.current_epoch = 0
    
    # ============ Required Methods (Must Implement) ============
    
    @abstractmethod
    def reset_episode(self) -> None:
        """Reset environment for a new episode"""
        pass
    
    @abstractmethod
    def get_states(self) -> Dict[str, Any]:
        """
        Get current state observation for all agents
        
        Returns:
            Dictionary mapping agent names to their state observations
        """
        pass
    
    @abstractmethod
    def execute_actions(self, actions: Dict[str, int]) -> None:
        """
        Execute actions for all agents in the environment
        
        Args:
            actions: Dictionary mapping agent names to action indices
        """
        pass
    
    @abstractmethod
    def get_default_reward_function(self) -> Callable:
        """
        Get the default reward function for this environment
        
        Returns:
            Function with signature: reward_fn(board, agent_name, **kwargs) -> float
        """
        pass
    
    @abstractmethod
    def get_default_termination_condition(self) -> Callable:
        """
        Get the default termination condition for this environment
        
        Returns:
            Function with signature: termination_fn(board, step, **kwargs) -> bool
        """
        pass
    
    # ============ Optional Methods (Can Override) ============
    
    def check_done(self, step: int) -> Dict[str, bool]:
        """
        Check if episode is done for each agent
        
        Args:
            step: Current step number
            
        Returns:
            Dictionary mapping agent names to done flags
        """
        # Default: use termination condition
        termination_fn = self.get_default_termination_condition()
        is_done = termination_fn(self.board, step)
        return {name: is_done for name in self.agents.keys()}
    
    def render_init(self, runner) -> None:
        """Initialize rendering setup"""
        pass

    def render(self, runner) -> None:
        """Render the current environment state"""
        # Default: try to render board if it has a render method
        if hasattr(self.board, 'render'):
            self.board.render()
        elif hasattr(self.board, 'board'):
            plt.clf()
            plt.imshow(self.board.board, cmap='gray')
            plt.pause(0.001)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get additional info about current state (optional)
        
        Returns:
            Dictionary with custom information
        """
        return {}
    
    # ============ Utility Methods ============
    
    def state_to_index(self, state: Any) -> int:
        """
        Convert state to index (for discrete state spaces)
        Override if environment uses discrete states
        """
        raise NotImplementedError("This environment doesn't use discrete state indexing")
    
    def index_to_state(self, index: int) -> Any:
        """
        Convert index to state (for discrete state spaces)
        Override if environment uses discrete states
        """
        raise NotImplementedError("This environment doesn't use discrete state indexing")