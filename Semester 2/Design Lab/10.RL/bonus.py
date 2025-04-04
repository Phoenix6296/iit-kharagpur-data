import gym
import numpy as np
import pygame
import time
import os
import random
from gym import spaces
from itertools import product

# --- Q-Learning Functions ---
def get_state_index(state, size):
    # Here state is defined as (robot_x, robot_y, dirt_1_x, dirt_1_y, dirt_2_x, dirt_2_y, ...)
    # For simplicity we flatten the state tuple. (Note: for many dirt cells the state space grows.)
    return sum([val * (size ** i) for i, val in enumerate(state)])

def choose_action(state, q_table, epsilon, action_space, size):
    if np.random.rand() < epsilon:
        return action_space.sample()
    state_idx = get_state_index(state, size)
    return np.argmax(q_table[state_idx])

def learn(q_table, state, action, reward, next_state, lr, gamma, size):
    s_idx = get_state_index(state, size)
    ns_idx = get_state_index(next_state, size)
    old_val = q_table[s_idx, action]
    q_table[s_idx, action] = (1 - lr) * old_val + lr * (reward + gamma * np.max(q_table[ns_idx]))

# --- Environment Class with Multiple Dirt Cells ---
class CleaningRobotEnv:
    def __init__(self, size=10, num_obstacles=5, num_dirt=3, max_steps=200):
        self.size = size
        self.max_steps = max_steps
        self.step_count = 0
        self.grid = np.zeros((size, size), dtype=np.uint8)
        self.place_obstacles(num_obstacles)
        self.dirt_positions = []   # list of positions (tuples) where dirt is present
        self.place_dirt_near_walls(num_dirt)
        self.robot_pos = None
        self.reset_env()

        # For large grids, use sparse representation
        self.large_grid = size > 1000
        if self.large_grid:
            self.obstacle_positions = set()
            for i in range(size):
                for j in range(size):
                    if self.grid[i, j] == 1:
                        self.obstacle_positions.add((i, j))

        self.action_space = spaces.Discrete(5)  # 4 movement + clean
        # Define observation state: robot position plus all dirt positions flattened
        obs_length = 2 + 2 * len(self.dirt_positions)
        self.observation_space = spaces.Box(low=0, high=size - 1, shape=(obs_length,), dtype=np.int32)

        # Only initialize pygame for smaller grids
        if size <= 100:
            pygame.init()
            self.cell_size = min(800 // size, 40)
            self.screen_size = self.size * self.cell_size
            self.screen_height = self.screen_size + 40
            self.screen = pygame.display.set_mode((self.screen_size, self.screen_height), pygame.DOUBLEBUF)
            pygame.display.set_caption("Cleaning Robot")
            self.clock = pygame.time.Clock()
            self.bg_color = (30, 30, 30)
            self.grid_color = (80, 80, 80)
            self.wall_color = (70, 70, 70)
            self.dirt_color = (255, 165, 0)
            self.robot_color = (0, 200, 200)
            self.font = pygame.font.SysFont("Arial", 20)
        else:
            self.screen = None

        self.current_action = None
        self.current_reward = 0

    def place_obstacles(self, num_obstacles):
        # Border walls
        self.grid[0, :] = self.grid[-1, :] = 1
        self.grid[:, 0] = self.grid[:, -1] = 1
        # Place additional obstacles in the interior
        obstacles_placed = 0
        while obstacles_placed < num_obstacles:
            x, y = np.random.randint(1, self.size - 1, size=2)
            if self.grid[x, y] == 0:
                self.grid[x, y] = 1
                obstacles_placed += 1

    def place_dirt_near_walls(self, num_dirt):
        """Place several dirt cells preferentially near walls/obstacles."""
        self.dirt_positions = []
        candidates = []
        wall_positions = np.argwhere(self.grid == 1)
        for wall_x, wall_y in wall_positions:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                x, y = wall_x + dx, wall_y + dy
                if (0 <= x < self.size and 0 <= y < self.size and self.grid[x, y] == 0):
                    candidates.append((x, y))
        # Remove duplicates and randomize candidates
        candidates = list(set(candidates))
        if not candidates:
            candidates = [(x, y) for x in range(self.size) 
                          for y in range(self.size) if self.grid[x, y] == 0]
        # Weight candidates by closeness to a wall
        weights = []
        for x, y in candidates:
            min_dist = min(abs(x - wx) + abs(y - wy) for wx, wy in wall_positions)
            weights.append(1 / (min_dist + 1))
        weights = np.array(weights)
        weights /= weights.sum()
        chosen = np.random.choice(len(candidates), size=min(num_dirt, len(candidates)), replace=False, p=weights)
        for idx in chosen:
            pos = candidates[idx]
            self.dirt_positions.append(pos)
            self.grid[pos] = 2  # mark dirt on the grid

    def reset_env(self):
        self.step_count = 0
        # Reset dirt: reposition dirt cells (if desired you could also keep them persistent)
        # For this implementation we reset the grid's dirt markers.
        for pos in self.dirt_positions:
            self.grid[pos] = 2
        # Place robot in an interior cell not adjacent to a wall and not on dirt.
        while True:
            x, y = np.random.randint(1, self.size - 1, size=2)
            if self.grid[x, y] == 0 and (x, y) not in self.dirt_positions:
                wall_adjacent = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if self.grid[x + dx, y + dy] == 1:
                        wall_adjacent = True
                        break
                if not wall_adjacent:
                    self.robot_pos = (x, y)
                    break
        self.current_action = None
        self.current_reward = 0
        # Build the state: robot position followed by flattened dirt positions.
        state = [self.robot_pos[0], self.robot_pos[1]]
        for dirt in self.dirt_positions:
            state.extend(dirt)
        return np.array(state, dtype=np.int32)

    def step_env(self, action):
        x, y = self.robot_pos
        reward = -1
        done = False

        if action < 4:  # Movement actions
            dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][action]
            new_x, new_y = x + dx, y + dy
            if self.large_grid:
                collision = (new_x < 0 or new_x >= self.size or 
                             new_y < 0 or new_y >= self.size or 
                             (new_x, new_y) in self.obstacle_positions)
            else:
                collision = self.grid[new_x, new_y] == 1
            if not collision:
                self.robot_pos = (new_x, new_y)
        elif action == 4:  # Clean action
            if self.robot_pos in self.dirt_positions:
                reward = 100
                self.dirt_positions.remove(self.robot_pos)
                self.grid[self.robot_pos] = 0  # Remove dirt from the grid
                if len(self.dirt_positions) == 0:
                    done = True  # Episode done if all dirt is cleared
            else:
                reward = -5

        self.current_action = action
        self.current_reward = reward
        self.step_count += 1
        if self.step_count >= self.max_steps:
            done = True

        # Build next state
        state = [self.robot_pos[0], self.robot_pos[1]]
        for dirt in self.dirt_positions:
            state.extend(dirt)
        # Pad with -1 if there are fewer dirt cells than initially
        initial_dirt = (self.observation_space.shape[0] - 2) // 2
        while len(state) < 2 + 2 * initial_dirt:
            state.extend([-1, -1])
        return np.array(state, dtype=np.int32), reward, done, {}

    def render(self, mode='human'):
        if self.size > 100:
            return np.zeros((1, 1, 3)) if mode == 'rgb_array' else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        self.screen.fill(self.bg_color)
        for i in range(self.size):
            for j in range(self.size):
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size, 
                                     self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.grid_color, rect, 1)
                if self.grid[i, j] == 1:
                    pygame.draw.rect(self.screen, self.wall_color, rect)
        # Draw all dirt positions
        for dirt in self.dirt_positions:
            rect = pygame.Rect(dirt[1] * self.cell_size, dirt[0] * self.cell_size, 
                               self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, self.dirt_color, rect)
        # Draw robot
        robot_center = (self.robot_pos[1] * self.cell_size + self.cell_size // 2,
                        self.robot_pos[0] * self.cell_size + self.cell_size // 2)
        radius = self.cell_size // 2 - 2
        pygame.draw.circle(self.screen, self.robot_color, robot_center, radius)
        # Info Panel
        info_panel = pygame.Surface((self.screen_size, 40), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 150))
        action_names = ['Up', 'Right', 'Down', 'Left', 'Clean']
        info_text = f"Action: {action_names[self.current_action] if self.current_action is not None else 'None'} | Reward: {self.current_reward} | Step: {self.step_count}"
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        info_panel.blit(text_surface, (10, 10))
        self.screen.blit(info_panel, (0, self.screen_size))
        pygame.display.flip()
        self.clock.tick(30)
        if mode == 'rgb_array':
            return np.transpose(pygame.surfarray.array3d(self.screen), (1, 0, 2))
        return None

# --- Example Main Loop Using Q-Learning or DQN ---
if __name__ == "__main__":
    total_start = time.time()  # Start global timer

    # Here we use the same hyperparameter search configuration for Q-Learning as before.
    config = {
        'grid_sizes': [10],
        'learning_rates': [0.1],
        'discount_factors': [0.9],
        'epsilons': [0.05, 0.1, 0.2, 0.4, 0.5],
        'max_steps_values': [10, 100, 1000, 10000, 100000],
    }
    
    episodes = 1000
    results = []
    best_results = {}
    best_params = {}

    for size in config['grid_sizes']:
        num_obstacles = max(5, size // 10)
        
        # Adjust parameters based on grid size (for small grids in this example)
        lr_options = config['learning_rates']
        gamma_options = config['discount_factors']
        eps_options = config['epsilons']
        steps_options = config['max_steps_values']

        for lr, gamma, eps, steps in product(lr_options, gamma_options, eps_options, steps_options):
            print(f"\nParams: grid_size={size}, lr={lr}, gamma={gamma}, epsilon={eps}, max_steps={steps}")
            
            state_space_size = size ** (2 + 2 * 3)  # robot position + dirt for 3 dirt cells
            q_table = np.zeros((state_space_size, 5))
                
            env = CleaningRobotEnv(size=size, num_obstacles=num_obstacles, num_dirt=3)
            rewards = []
            start_time_config = time.time()  # Timer for this configuration

            for ep in range(episodes):
                state = env.reset_env()
                total_reward = 0
                
                for _ in range(steps):
                    action = choose_action(state, q_table, eps, env.action_space, size)
                    next_state, reward, done, _ = env.step_env(action)
                    
                    learn(q_table, state, action, reward, next_state, lr, gamma, size)
                    
                    state = next_state
                    total_reward += reward
                    
                    if ep % 100 == 0 and size <= 100:
                        env.render()
                    
                    if done:
                        break
                
                rewards.append(total_reward)
                if ep % 100 == 0:
                    print(f"Episode {ep}, Total Reward: {total_reward}")

            time_taken_config = time.time() - start_time_config
            final_avg_reward = np.mean(rewards[-100:]) if rewards else 0
            result_config = {
                'grid_size': size,
                'lr': lr,
                'gamma': gamma,
                'epsilon': eps,
                'max_steps': steps,
                'final_avg_reward': final_avg_reward,
                'time_taken': time_taken_config
            }
            results.append(result_config)

            if size not in best_results or final_avg_reward > best_results[size]['final_avg_reward']:
                best_results[size] = {'final_avg_reward': final_avg_reward}
                best_params[size] = result_config
                os.makedirs("models/q_learning", exist_ok=True)
                if size <= 100:
                    np.save(f"models/q_learning/best_model_{size}.npy", q_table)

    for size, params in best_params.items():
        print(f"\nBest params for grid size {size}:")
        print(params)

    if any(size <= 100 for size in config['grid_sizes']):
        pygame.quit()

    total_time = time.time() - total_start  # Total global execution time
    print(f"\nTotal execution time: {total_time:.2f} seconds")