# environment.py

import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class RoomCleaningEnv(gym.Env):
    """
    Custom environment for a room cleaning robot with visual rendering,
    multiple obstacles, and modified border movement.
    
    Grid representation:
      - 'W' denotes the walls on the border.
      - 'O' denotes obstacles inside the grid.
      - ' ' denotes free cells.
      - 'D' denotes the dirt patch (only one per episode).
      - 'A' denotes the agent's current position (for rendering).
      
    Actions:
      0: move up
      1: move right
      2: move down
      3: move left
      4: clean (attempt cleaning the current cell)
      
    Rewards:
      - Base movement cost: -1 per step.
      - Hitting an obstacle or trying to move out-of-bound: -5.
      - Bonus for moving closer to the dirt patch.
      - Successful cleaning: +10 and episode ends.
      - Cleaning an empty cell: -2.
      
    Border Behavior:
      - If the agent is on a border and takes an action that would move it out, the agent stays in the same cell.
    
    The episode ends when either the dirt is cleaned or the maximum steps are reached.
    """
    
    metadata = {'render.modes': ['human', 'visual']}
    
    def __init__(self, grid_size=10, max_steps=100, num_obstacles=5):
        super(RoomCleaningEnv, self).__init__()
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.num_obstacles = num_obstacles
        
        # Define action space (5 discrete actions)
        self.action_space = spaces.Discrete(5)
        
        # Observation space: (agent_x, agent_y, dirt_cleaned_flag)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(self.grid_size),
            spaces.Discrete(self.grid_size),
            spaces.Discrete(2)
        ))
        
        self.current_step = 0
        self._build_room()
        
        # Setup matplotlib for interactive visualization
        plt.ion()
        self.fig = plt.figure(figsize=(5,5))
    
    def _build_room(self):
        # Create grid with free spaces
        self.grid = np.full((self.grid_size, self.grid_size), ' ', dtype=str)
        
        # Set borders as walls
        self.grid[0, :] = 'W'
        self.grid[-1, :] = 'W'
        self.grid[:, 0] = 'W'
        self.grid[:, -1] = 'W'
        
        # Place obstacles randomly in the interior (avoid borders)
        possible_positions = [(i, j) for i in range(1, self.grid_size - 1)
                              for j in range(1, self.grid_size - 1)]
        np.random.shuffle(possible_positions)
        for pos in possible_positions[:self.num_obstacles]:
            self.grid[pos] = 'O'
        
        # Place the dirt patch in one of the cells adjacent to a wall (and free)
        possible_dirt = []
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                if (i == 1 or i == self.grid_size - 2 or j == 1 or j == self.grid_size - 2) and self.grid[i, j] == ' ':
                    possible_dirt.append((i, j))
        if possible_dirt:
            self.dirt_position = possible_dirt[np.random.randint(len(possible_dirt))]
            self.grid[self.dirt_position] = 'D'
        else:
            self.dirt_position = (1, 1)
            self.grid[self.dirt_position] = 'D'
        
        self.dirt_cleaned = False
        
        # Set agent's starting position: center if free; otherwise, first free cell.
        center = (self.grid_size // 2, self.grid_size // 2)
        if self.grid[center] in [' ', 'D']:
            self.agent_position = center
        else:
            free_positions = [(i, j) for i in range(1, self.grid_size - 1)
                              for j in range(1, self.grid_size - 1) if self.grid[i, j] == ' ']
            self.agent_position = free_positions[0] if free_positions else center
    
    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def reset(self):
        """Reset the environment to the initial state."""
        self.current_step = 0
        self._build_room()
        return self._get_obs()
    
    def _get_obs(self):
        """Return current observation."""
        return (self.agent_position[0], self.agent_position[1], int(self.dirt_cleaned))
    
    def _can_move(self, pos):
        """Return True if pos is within bounds and not a wall or obstacle."""
        x, y = pos
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
        if self.grid[x, y] in ['W', 'O']:
            return False
        return True
    
    def step(self, action):
        """
        Execute one step.
        For movement actions, if the move is illegal (out-of-bound, obstacle, or border action),
        the agent remains in the same cell.
        """
        self.current_step += 1
        base_reward = -1  # Base movement cost
        reward = base_reward
        done = False
        info = {}
        
        x, y = self.agent_position
        prev_distance = self._manhattan_distance((x, y), self.dirt_position)
        
        # Determine next position based on action.
        if action == 0:      # Up
            new_pos = (x - 1, y)
        elif action == 1:    # Right
            new_pos = (x, y + 1)
        elif action == 2:    # Down
            new_pos = (x + 1, y)
        elif action == 3:    # Left
            new_pos = (x, y - 1)
        elif action == 4:    # Clean
            if (x, y) == self.dirt_position and not self.dirt_cleaned:
                self.dirt_cleaned = True
                reward = 10
                done = True
            else:
                reward = -2
            new_pos = (x, y)
        else:
            raise ValueError("Invalid action.")
        
        # Process movement action
        if action in [0, 1, 2, 3]:
            if not self._can_move(new_pos):
                # Illegal move penalty
                new_pos = (x, y)
                reward = -5
            self.agent_position = new_pos
        
        # Shaping: Bonus for moving closer to the dirt patch.
        new_distance = self._manhattan_distance(self.agent_position, self.dirt_position)
        if new_distance < prev_distance:
            reward += 0.5
        
        if self.current_step >= self.max_steps:
            done = True
        
        return self._get_obs(), reward, done, info
    
    def render_visual(self, action=None, reward=0, pause_time=0.5):
        """Render the current grid state using matplotlib."""
        # Map grid symbols to numbers:
        # 0: Wall, 1: Free, 2: Dirt, 3: Obstacle, 4: Agent.
        vis_grid = np.zeros((self.grid_size, self.grid_size))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] == 'W':
                    vis_grid[i, j] = 0
                elif self.grid[i, j] == ' ':
                    vis_grid[i, j] = 1
                elif self.grid[i, j] == 'D':
                    vis_grid[i, j] = 2
                elif self.grid[i, j] == 'O':
                    vis_grid[i, j] = 3
        # Mark the agent's position
        x, y = self.agent_position
        vis_grid[x, y] = 4
        
        cmap = mcolors.ListedColormap(['black', 'white', 'saddlebrown', 'gray', 'blue'])
        bounds = [0, 1, 2, 3, 4, 5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        
        plt.imshow(vis_grid, cmap=cmap, norm=norm)
        plt.title(f"Step: {self.current_step} | Action: {action} | Reward: {reward}")
        plt.xticks([])
        plt.yticks([])
        plt.pause(pause_time)
        plt.clf()
