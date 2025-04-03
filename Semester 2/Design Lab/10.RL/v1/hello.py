import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import itertools
import time

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
        # When dirt is cleaned, we return (-1, -1) for dirt position.
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
        # If dirt is cleaned, mark dirt_pos as (-1,-1)
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

def q_learning_train(env, alpha, gamma, epsilon, max_steps, num_episodes=500):
    """
    Train a Q-learning agent on the provided environment.
    Returns the Q-table and a list of total rewards per episode.
    """
    # Use a dictionary for the Q-table with state tuple as key.
    Q = {}
    
    def get_Q(state, action):
        return Q.get((state, action), 0.0)
    
    def set_Q(state, action, value):
        Q[(state, action)] = value
    
    rewards_per_episode = []
    
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        
        for step in range(max_steps):
            # Epsilon-greedy action selection
            if np.random.rand() < epsilon:
                action = env.action_space.sample()
            else:
                # Choose action with highest Q value (if tie, choose randomly)
                q_values = [get_Q(state, a) for a in range(env.action_space.n)]
                max_val = max(q_values)
                # Get all actions with maximum Q-value
                actions_with_max = [a for a, q in enumerate(q_values) if q == max_val]
                action = np.random.choice(actions_with_max)
            
            next_state, reward, done, _ = env.step(action)
            total_reward += reward
            
            # Q-learning update rule
            q_next = [get_Q(next_state, a) for a in range(env.action_space.n)]
            td_target = reward + gamma * max(q_next) if not done else reward
            new_value = get_Q(state, action) + alpha * (td_target - get_Q(state, action))
            set_Q(state, action, new_value)
            
            state = next_state
            
            if done:
                break
        rewards_per_episode.append(total_reward)
    
    return Q, rewards_per_episode

if __name__ == '__main__':
    env = CleaningRobotEnv(grid_size=10)
    
    # Define hyperparameter candidate values
    learning_rates = [0.1, 0.5]         # candidate α values
    discount_factors = [0.9, 0.95]        # candidate γ values
    exploration_rates = [0.05, 0.1, 0.2, 0.4, 0.5]  # candidate ε values
    max_steps_list = [10, 100, 1000, 10000, 100000]   # candidate max steps per episode
    
    num_episodes = 500  # number of episodes for each hyperparameter combination
    
    # Store results: key is tuple of hyperparameters, value is average reward
    results = {}
    
    # Grid search over hyperparameters
    total_combinations = len(learning_rates) * len(discount_factors) * len(exploration_rates) * len(max_steps_list)
    combo_counter = 1
    for alpha, gamma, epsilon, max_steps in itertools.product(learning_rates,
                                                                discount_factors,
                                                                exploration_rates,
                                                                max_steps_list):
        print(f"Running combination {combo_counter}/{total_combinations}: "
              f"alpha={alpha}, gamma={gamma}, epsilon={epsilon}, max_steps={max_steps}")
        start_time = time.time()
        _, rewards = q_learning_train(env, alpha, gamma, epsilon, max_steps, num_episodes=num_episodes)
        avg_reward = np.mean(rewards)
        results[(alpha, gamma, epsilon, max_steps)] = avg_reward
        elapsed = time.time() - start_time
        print(f"Average reward: {avg_reward:.2f} (elapsed time: {elapsed:.2f} sec)\n")
        combo_counter += 1

    # Find the best hyperparameter combination based on average reward
    best_params = max(results, key=results.get)
    best_avg_reward = results[best_params]
    
    print("Grid Search Results:")
    for params, avg_r in results.items():
        print(f"alpha={params[0]}, gamma={params[1]}, epsilon={params[2]}, max_steps={params[3]} -> Avg Reward: {avg_r:.2f}")
    
    print("\nBest Hyperparameters:")
    print(f"alpha={best_params[0]}, gamma={best_params[1]}, epsilon={best_params[2]}, max_steps={best_params[3]} with Avg Reward: {best_avg_reward:.2f}")
    
    # Optional: run one final demonstration episode with the best hyperparameters
    print("\nDemonstration with the best hyperparameters:")
    Q_best, _ = q_learning_train(env, best_params[0], best_params[1], best_params[2], best_params[3], num_episodes=1000)
    state = env.reset()
    env.render()
    done = False
    total_demo_reward = 0
    while not done:
        # Choose the best action according to Q_best
        q_values = [Q_best.get((state, a), 0.0) for a in range(env.action_space.n)]
        max_val = max(q_values)
        actions_with_max = [a for a, q in enumerate(q_values) if q == max_val]
        action = np.random.choice(actions_with_max)
        state, reward, done, _ = env.step(action)
        total_demo_reward += reward
        env.render()
        plt.pause(0.2)
    print("Demonstration episode finished with total reward:", total_demo_reward)
    env.close()
