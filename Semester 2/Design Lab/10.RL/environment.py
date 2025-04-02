# environment.py

import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class RoomCleaningEnv(gym.Env):
    """
    A custom environment for a room cleaning robot with visual rendering.
    
    Grid representation:
      - 'W' denotes walls (boundaries)
      - ' ' denotes empty/free cells
      - 'D' denotes the dirt patch (only one per episode)
      - The agent's current position is rendered as 'A'
      
    Actions:
      0: move up
      1: move right
      2: move down
      3: move left
      4: clean (attempt to clean the current cell)
      
    Rewards:
      - Moving: -1 per step.
      - Hitting a wall (illegal move): -5.
      - Cleaning when dirt is present: +10 and episode ends.
      - Cleaning on an empty cell: -2.
      
    The episode ends when either the dirt is cleaned or the maximum number of steps is reached.
    """
    
    metadata = {'render.modes': ['human', 'visual']}
    
    def __init__(self, grid_size=10, max_steps=100):
        super(RoomCleaningEnv, self).__init__()
        self.grid_size = grid_size
        self.max_steps = max_steps
        
        # Define action space: 5 discrete actions (up, right, down, left, clean)
        self.action_space = spaces.Discrete(5)
        
        # Define observation space:
        # (agent_x, agent_y, dirt_cleaned_flag) where dirt_cleaned_flag is 0 (not cleaned) or 1 (cleaned)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(self.grid_size),
            spaces.Discrete(self.grid_size),
            spaces.Discrete(2)
        ))
        
        self.current_step = 0
        self._build_room()
        
        # Set up Matplotlib for interactive visualization
        plt.ion()
        self.fig = plt.figure(figsize=(5,5))
    
    def _build_room(self):
        # Create a grid with all free spaces
        self.grid = np.full((self.grid_size, self.grid_size), ' ', dtype=str)
        
        # Set the boundaries as walls
        self.grid[0, :] = 'W'
        self.grid[-1, :] = 'W'
        self.grid[:, 0] = 'W'
        self.grid[:, -1] = 'W'
        
        # Place a single dirt cell in one of the cells adjacent to a wall (but not on a wall)
        possible_dirt = []
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                if i == 1 or i == self.grid_size - 2 or j == 1 or j == self.grid_size - 2:
                    possible_dirt.append((i, j))
        self.dirt_position = possible_dirt[np.random.randint(len(possible_dirt))]
        self.grid[self.dirt_position] = 'D'
        self.dirt_cleaned = False
        
        # Set the agent's initial position at the center; if that coincides with dirt, shift by one.
        self.agent_position = (self.grid_size // 2, self.grid_size // 2)
        if self.agent_position == self.dirt_position:
            self.agent_position = (self.agent_position[0] + 1, self.agent_position[1])
    
    def reset(self):
        """Reset the environment to the initial state."""
        self.current_step = 0
        self._build_room()
        return self._get_obs()
    
    def _get_obs(self):
        """Return the current observation: agent position and dirt status."""
        return (self.agent_position[0], self.agent_position[1], int(self.dirt_cleaned))
    
    def step(self, action):
        """
        Execute one time step within the environment.
        
        Parameters:
          action (int): An integer representing the action to take.
          
        Returns:
          observation (tuple): The new state.
          reward (float): The reward received.
          done (bool): Whether the episode has ended.
          info (dict): Additional information.
        """
        self.current_step += 1
        reward = -1  # default movement cost
        done = False
        info = {}
        
        x, y = self.agent_position
        
        if action == 0:      # Move Up
            new_pos = (x - 1, y)
        elif action == 1:    # Move Right
            new_pos = (x, y + 1)
        elif action == 2:    # Move Down
            new_pos = (x + 1, y)
        elif action == 3:    # Move Left
            new_pos = (x, y - 1)
        elif action == 4:    # Clean
            if (x, y) == self.dirt_position and not self.dirt_cleaned:
                self.dirt_cleaned = True
                reward = 10  # reward for successful cleaning
                done = True
            else:
                reward = -2  # penalty for trying to clean an empty cell
            new_pos = (x, y)  # no movement when cleaning
        else:
            raise ValueError("Invalid action.")
        
        if action in [0, 1, 2, 3]:
            if self._is_valid(new_pos):
                self.agent_position = new_pos
            else:
                reward = -5  # penalty for attempting to move into a wall
        
        if self.current_step >= self.max_steps:
            done = True
        
        return self._get_obs(), reward, done, info
    
    def _is_valid(self, pos):
        """Check whether a position is within bounds and not a wall."""
        x, y = pos
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
        if self.grid[x, y] == 'W':
            return False
        return True
    
    def render_visual(self, action=None, reward=0, pause_time=0.5):
        """
        Visual rendering of the environment using Matplotlib.
        
        The visualization includes:
          - Walls (black)
          - Free spaces (white)
          - Dirt patch (brown)
          - Agent (blue)
        It overlays the current action, reward, and step count.
        """
        vis_grid = np.zeros((self.grid_size, self.grid_size))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 'W':
                    vis_grid[i, j] = 0
                elif self.grid[i, j] == ' ':
                    vis_grid[i, j] = 1
                elif self.grid[i, j] == 'D':
                    vis_grid[i, j] = 2
        
        x, y = self.agent_position
        vis_grid[x, y] = 3
        
        cmap = mcolors.ListedColormap(['black', 'white', 'saddlebrown', 'blue'])
        bounds = [0, 1, 2, 3, 4]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        
        plt.imshow(vis_grid, cmap=cmap, norm=norm)
        plt.title(f"Step: {self.current_step} | Action: {action} | Reward: {reward}")
        plt.xticks([])
        plt.yticks([])
        plt.pause(pause_time)
        plt.clf()
