import gym
import numpy as np
import pygame
import time
import os
from gym import spaces
from itertools import product
import argparse

# --- Q-Learning Functions ---
def get_state_index(state, size):
    rx, ry, dx, dy = state
    return rx * size**3 + ry * size**2 + dx * size + dy

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

# --- Environment Class ---
class CleaningRobotEnv:
    def __init__(self, size=10, num_obstacles=5, visualize=False, delay=0.1):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.uint8)
        self.place_obstacles(num_obstacles)
        self.dirt_pos = None
        self.place_dirt_near_walls()
        self.robot_pos = None
        self.reset_env()

        # For large grids, use sparse representation
        self.large_grid = size > 1000
        if self.large_grid:
            self.obstacle_positions = set()
            for i in range(size):
                for j in range(size):
                    if self.grid[i,j] == 1:
                        self.obstacle_positions.add((i,j))

        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=size - 1, shape=(4,), dtype=np.int32)

        # Only initialize pygame for smaller grids
        self.visualize = visualize
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
        self.step_count = 0
        self.delay = delay  # delay for visualization

    def place_obstacles(self, num_obstacles):
        # Border walls
        self.grid[0, :] = self.grid[-1, :] = 1
        self.grid[:, 0] = self.grid[:, -1] = 1
        
        # Place additional obstacles
        obstacles_placed = 0
        while obstacles_placed < num_obstacles:
            x, y = np.random.randint(1, self.size - 1, size=2)
            if self.grid[x, y] == 0:
                self.grid[x, y] = 1
                obstacles_placed += 1

    def place_dirt_near_walls(self):
        """Place dirt preferentially near walls/obstacles"""
        candidates = []
        wall_positions = np.argwhere(self.grid == 1)
        
        for wall_x, wall_y in wall_positions:
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                x, y = wall_x + dx, wall_y + dy
                if (0 <= x < self.size and 0 <= y < self.size and 
                    self.grid[x,y] == 0 and (x,y) != self.dirt_pos):
                    candidates.append((x,y))
        
        if not candidates:
            candidates = [(x,y) for x in range(self.size) 
                         for y in range(self.size) if self.grid[x,y] == 0]
        
        if candidates:
            weights = []
            for x,y in candidates:
                min_dist = min(abs(x-wx) + abs(y-wy) for wx,wy in wall_positions)
                weights.append(1/(min_dist + 1))
            
            weights = np.array(weights)
            weights /= weights.sum()
            idx = np.random.choice(len(candidates), p=weights)
            self.dirt_pos = candidates[idx]
            self.grid[self.dirt_pos] = 2

    def reset_env(self):
        # Place robot away from walls and dirt
        while True:
            x, y = np.random.randint(1, self.size - 1, size=2)
            if self.grid[x, y] == 0 and (x,y) != self.dirt_pos:
                wall_adjacent = False
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    if self.grid[x+dx, y+dy] == 1:
                        wall_adjacent = True
                        break
                if not wall_adjacent:
                    self.robot_pos = (x, y)
                    break
        
        self.current_action = None
        self.current_reward = 0
        self.step_count = 0
        return np.array([*self.robot_pos, *self.dirt_pos], dtype=np.int32)

    def step_env(self, action):
        x, y = self.robot_pos
        reward = -1
        done = False

        if action < 4:
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
        elif action == 4:
            if self.robot_pos == self.dirt_pos:
                reward = 100
                done = True
                self.grid[self.dirt_pos] = 0
            else:
                reward = -5

        self.current_action = action
        self.current_reward = reward
        self.step_count += 1

        state = np.array([*self.robot_pos, *self.dirt_pos], dtype=np.int32)
        return state, reward, done, {}

    def render(self, mode='human'):
        if self.size > 100:
            return np.zeros((1,1,3)) if mode == 'rgb_array' else None

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
                elif (i, j) == self.dirt_pos:
                    pygame.draw.rect(self.screen, self.dirt_color, rect)

        robot_center = (self.robot_pos[1] * self.cell_size + self.cell_size // 2,
                        self.robot_pos[0] * self.cell_size + self.cell_size // 2)
        radius = self.cell_size // 2 - 2
        pygame.draw.circle(self.screen, self.robot_color, robot_center, radius)

        info_panel = pygame.Surface((self.screen_size, 40), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 150))
        action_names = ['Up', 'Right', 'Down', 'Left', 'Clean']
        info_text = f"Action: {action_names[self.current_action] if self.current_action is not None else 'None'} | Reward: {self.current_reward} | Step: {self.step_count}"
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        info_panel.blit(text_surface, (10, 10))
        self.screen.blit(info_panel, (0, self.screen_size))
        pygame.display.flip()
        self.clock.tick(30)
        if self.visualize:
            time.sleep(self.delay)
        if mode == 'rgb_array':
            return np.transpose(pygame.surfarray.array3d(self.screen), (1, 0, 2))
        return None

# --- Q-Learning Main Loop ---
def run_qlearning(env, episodes, lr, gamma, epsilon, max_steps, q_table=None):
    size = env.size
    if q_table is None:
        if size > 100:
            q_table = {}  # Use dictionary for large grids
        else:
            state_size = size ** 4
            q_table = np.zeros((state_size, 5))
    rewards = []
    for ep in range(episodes):
        state = env.reset_env()
        total_reward = 0
        
        for _ in range(max_steps):
            action = choose_action(state, q_table, epsilon, env.action_space, size)
            next_state, reward, done, _ = env.step_env(action)
            
            if size > 100:
                s_idx = tuple(state)
                ns_idx = tuple(next_state)
                if s_idx not in q_table:
                    q_table[s_idx] = np.zeros(5)
                if ns_idx not in q_table:
                    q_table[ns_idx] = np.zeros(5)
                old_val = q_table[s_idx][action]
                q_table[s_idx][action] = (1 - lr) * old_val + lr * (reward + gamma * np.max(q_table[ns_idx]))
            else:
                learn(q_table, state, action, reward, next_state, lr, gamma, size)
            
            state = next_state
            total_reward += reward
            
            if env.visualize and env.size <= 100:
                env.render()
            
            if done:
                break
        rewards.append(total_reward)
    return q_table, rewards

# --- Main Section ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hyperparameter", action="store_true",
                        help="Run hyperparameter tuning with provided config for each grid size")
    parser.add_argument("--evaluate", action="store_true",
                        help="Evaluate on multiple grid sizes. If only --evaluate is passed, use hardcoded parameters. If both --hyperparameter and --evaluate are passed, use tuned parameters.")
    parser.add_argument("--visualize", action="store_true",
                        help="Enable visualization with a delay")
    args = parser.parse_args()

    episodes = 1000  # Episodes per configuration

    # Default (hardcoded) parameters for training when no flag is provided:
    default_params = {
        'grid_size': 10,
        'lr': 0.1,
        'gamma': 0.9,
        'epsilon': 0.1,
        'max_steps': 1000,
    }

    tuned_params = {}  # Will hold tuned parameters for each grid size

    if args.hyperparameter:
        print("\nStarting hyperparameter tuning...")
        config = {
            'grid_sizes': [10, 100],
            'learning_rates': [0.1],
            'discount_factors': [0.9],
            'epsilons': [0.05, 0.1, 0.2, 0.4, 0.5],
            'max_steps_values': [10, 100, 1000, 10000, 100000],
        }
        for grid in config['grid_sizes']:
            print(f"\nTuning for grid size: {grid}")
            best_final_reward = -np.inf
            best_config = None
            for lr, gamma, eps, steps in product(config['learning_rates'],
                                                 config['discount_factors'],
                                                 config['epsilons'],
                                                 config['max_steps_values']):
                print(f"Tuning params: grid_size={grid}, lr={lr}, gamma={gamma}, epsilon={eps}, max_steps={steps}")
                env = CleaningRobotEnv(size=grid, num_obstacles=max(5, grid // 10), visualize=args.visualize)
                _, rewards = run_qlearning(env, episodes, lr, gamma, eps, steps)
                final_avg_reward = np.mean(rewards[-100:]) if rewards else -np.inf
                print(f"Final average reward: {final_avg_reward}")
                if final_avg_reward > best_final_reward:
                    best_final_reward = final_avg_reward
                    best_config = {'grid_size': grid, 'lr': lr, 'gamma': gamma, 'epsilon': eps, 'max_steps': steps}
            tuned_params[grid] = best_config
            print(f"Best hyperparameters for grid size {grid}: {best_config}")
    
    # Evaluation Phase
    if args.evaluate:
        print("\nStarting evaluation...")
        # Evaluation grid sizes: 10, 100, 1000, 10000, 100000, 1e7
        eval_sizes = [10, 100]
        for grid in eval_sizes:
            start_time = time.time()
            print(f"\nEvaluating on grid size: {grid}")
            # If hyperparameter tuning was done AND both flags are passed, use tuned parameters.
            if args.hyperparameter:
                if grid in tuned_params:
                    params = tuned_params[grid]
                else:
                    # Fallback: use parameters from the smallest tuned grid
                    params = tuned_params[min(tuned_params.keys())]
            else:
                params = default_params
            env = CleaningRobotEnv(size=grid, num_obstacles=max(5, grid // 10), visualize=args.visualize)
            _, rewards = run_qlearning(env, episodes,
                                       params['lr'],
                                       params['gamma'],
                                       params['epsilon'],
                                       params['max_steps'])
            avg_reward = np.mean(rewards[-100:]) if rewards else None
            elapsed = time.time() - start_time
            print(f"Grid size {grid}: Params: {params} | Average Reward (last 100 eps): {avg_reward}")
            print(f"Time taken for grid size {grid}: {elapsed:.2f} seconds")
    else:
        # If not evaluating, just train on grid size 10.
        if args.hyperparameter:
            grid_size = tuned_params[10]['grid_size']
            params = tuned_params[10]
        else:
            grid_size = default_params['grid_size']
            params = default_params
        env = CleaningRobotEnv(size=grid_size, num_obstacles=max(5, grid_size // 10), visualize=args.visualize)
        _, rewards = run_qlearning(env, episodes,
                                   params['lr'],
                                   params['gamma'],
                                   params['epsilon'],
                                   params['max_steps'])
        print(f"\nTraining complete for grid size {grid_size}!")
        print(f"Final average reward over last 100 episodes: {np.mean(rewards[-100:])}")

    # Cleanup: Quit pygame if used.
    if (args.evaluate and ( (args.hyperparameter and any(g <= 100 for g in tuned_params.keys())) or (not args.hyperparameter and default_params['grid_size'] <= 100) )) \
       or (not args.evaluate and (params['grid_size'] <= 100)):
        pygame.quit()
