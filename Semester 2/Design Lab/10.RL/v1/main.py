import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class CleaningRobotEnv(gym.Env):
    """
    Custom Environment for a cleaning robot in a grid world.
    The grid has boundaries (walls) and one dirt patch placed near the walls.
    The agent can move (up, down, left, right) or attempt to clean the current cell.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, grid_size=10):
        super(CleaningRobotEnv, self).__init__()
        self.grid_size = grid_size
        
        # Define action space: 0: up, 1: down, 2: left, 3: right, 4: clean
        self.action_space = spaces.Discrete(5)
        
        # Observation: (agent_row, agent_col, dirt_row, dirt_col)
        # When dirt is cleaned, we can return (-1, -1) for dirt position.
        self.observation_space = spaces.Tuple((
            spaces.Discrete(self.grid_size),
            spaces.Discrete(self.grid_size),
            spaces.Discrete(self.grid_size),
            spaces.Discrete(self.grid_size)
        ))
        
        # Internal state
        self.agent_pos = None
        self.dirt_pos = None
        self.done = False
        
        # Visualization elements
        self.fig = None
        self.ax = None

    def reset(self):
        # Reset the agent at a random position within the grid.
        self.agent_pos = np.array([np.random.randint(self.grid_size),
                                     np.random.randint(self.grid_size)])
        
        # Place dirt patch near one of the walls (i.e. first or last row/column)
        # Randomly choose one wall edge and then choose a random position along that edge.
        wall = np.random.choice(['top', 'bottom', 'left', 'right'])
        if wall == 'top':
            dirt_row = 0
            dirt_col = np.random.randint(self.grid_size)
        elif wall == 'bottom':
            dirt_row = self.grid_size - 1
            dirt_col = np.random.randint(self.grid_size)
        elif wall == 'left':
            dirt_col = 0
            dirt_row = np.random.randint(self.grid_size)
        else:  # right
            dirt_col = self.grid_size - 1
            dirt_row = np.random.randint(self.grid_size)
        
        self.dirt_pos = np.array([dirt_row, dirt_col])
        
        # Ensure the agent does not start on the dirt cell.
        while np.array_equal(self.agent_pos, self.dirt_pos):
            self.agent_pos = np.array([np.random.randint(self.grid_size),
                                         np.random.randint(self.grid_size)])
            
        self.done = False
        return self._get_obs()

    def _get_obs(self):
        # If dirt is cleaned, we mark dirt_pos as (-1,-1)
        if self.done:
            return (self.agent_pos[0], self.agent_pos[1], -1, -1)
        return (self.agent_pos[0], self.agent_pos[1], self.dirt_pos[0], self.dirt_pos[1])

    def step(self, action):
        if self.done:
            return self._get_obs(), 0, self.done, {}
        
        reward = -1  # step cost
        info = {}

        # Process actions for movement
        if action in [0, 1, 2, 3]:
            new_pos = self.agent_pos.copy()
            if action == 0:   # up
                new_pos[0] -= 1
            elif action == 1: # down
                new_pos[0] += 1
            elif action == 2: # left
                new_pos[1] -= 1
            elif action == 3: # right
                new_pos[1] += 1

            # Check for collision with walls (grid boundaries)
            if (0 <= new_pos[0] < self.grid_size) and (0 <= new_pos[1] < self.grid_size):
                self.agent_pos = new_pos
            else:
                # Penalize collision with wall, no movement is made.
                reward -= 5

        # Process cleaning action
        elif action == 4:
            if np.array_equal(self.agent_pos, self.dirt_pos):
                reward += 50  # successful cleaning
                self.done = True
            else:
                reward -= 10  # penalty for cleaning in a wrong place

        # Return observation, reward, done flag, and info.
        return self._get_obs(), reward, self.done, info

    def render(self, mode='human'):
        # Create grid visualization with matplotlib
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=(6, 6))
        
        self.ax.clear()
        
        # Draw grid lines
        for x in range(self.grid_size + 1):
            self.ax.axhline(x, lw=1, color='gray', zorder=1)
            self.ax.axvline(x, lw=1, color='gray', zorder=1)
        
        # Draw dirt patch if not cleaned
        if not self.done:
            dirt_patch = patches.Rectangle((self.dirt_pos[1], self.grid_size - 1 - self.dirt_pos[0]), 
                                           1, 1, facecolor='saddlebrown', edgecolor='black', lw=2, label='Dirt')
            self.ax.add_patch(dirt_patch)
        
        # Draw robot as a circle
        robot_circle = patches.Circle((self.agent_pos[1] + 0.5, self.grid_size - 1 - self.agent_pos[0] + 0.5), 
                                      0.3, facecolor='blue', edgecolor='black', lw=2, label='Robot')
        self.ax.add_patch(robot_circle)
        
        self.ax.set_title('Cleaning Robot Environment')
        self.ax.set_xlim(0, self.grid_size)
        self.ax.set_ylim(0, self.grid_size)
        self.ax.set_aspect('equal')
        self.ax.legend(loc='upper right')
        plt.pause(0.1)
        plt.draw()

    def close(self):
        if self.fig:
            plt.close(self.fig)


# Example usage:
if __name__ == '__main__':
    env = CleaningRobotEnv(grid_size=10)
    obs = env.reset()
    print("Initial Observation:", obs)
    done = False
    total_reward = 0

    # Run a random policy for demonstration
    while not done:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        total_reward += reward
        print("Action:", action, "Obs:", obs, "Reward:", reward, "Done:", done)
        env.render()
    print("Episode finished with total reward:", total_reward)
    env.close()
