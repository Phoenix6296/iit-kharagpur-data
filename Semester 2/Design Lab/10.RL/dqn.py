import gym
import numpy as np
import pygame
import time
import os
import random
from itertools import product
import torch
import torch.nn as nn
import torch.optim as optim
from gym import spaces
from collections import deque
import sys

# --- Environment Class (Same as before) ---
class CleaningRobotEnv:
    def __init__(self, size=10, num_obstacles=5, max_steps=200):
        self.size = size
        self.max_steps = max_steps
        self.step_count = 0
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
                    if self.grid[i, j] == 1:
                        self.obstacle_positions.add((i, j))

        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=size - 1, shape=(4,), dtype=np.int32)

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
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                x, y = wall_x + dx, wall_y + dy
                if (0 <= x < self.size and 0 <= y < self.size and 
                    self.grid[x, y] == 0 and (x, y) != self.dirt_pos):
                    candidates.append((x, y))
        if not candidates:
            candidates = [(x, y) for x in range(self.size) 
                          for y in range(self.size) if self.grid[x, y] == 0]
        if candidates:
            weights = []
            for x, y in candidates:
                min_dist = min(abs(x - wx) + abs(y - wy) for wx, wy in wall_positions)
                weights.append(1 / (min_dist + 1))
            weights = np.array(weights)
            weights /= weights.sum()
            idx = np.random.choice(len(candidates), p=weights)
            self.dirt_pos = candidates[idx]
            self.grid[self.dirt_pos] = 2

    def reset_env(self):
        self.step_count = 0
        while True:
            x, y = np.random.randint(1, self.size - 1, size=2)
            if self.grid[x, y] == 0 and (x, y) != self.dirt_pos:
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
        if self.step_count >= self.max_steps:
            done = True
        state = np.array([*self.robot_pos, *self.dirt_pos], dtype=np.int32)
        return state, reward, done, {}

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
        if mode == 'rgb_array':
            return np.transpose(pygame.surfarray.array3d(self.screen), (1, 0, 2))
        return None

# --- DQN Implementation ---
class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_size)
        )
    
    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, state_size, action_size, config):
        self.state_size = state_size
        self.action_size = action_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize the networks
        self.policy_net = DQN(state_size, action_size).to(self.device)
        self.target_net = DQN(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Hyperparameters from config
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=config['lr'])
        self.memory = deque(maxlen=int(config['replay_buffer_size']))
        self.batch_size = config['batch_size']
        self.gamma = config['gamma']
        self.epsilon = config['epsilon']
        self.epsilon_min = 0.01
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.update_frequency = config['update_frequency']
        self.steps_done = 0

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            action_values = self.policy_net(state_tensor)
        return torch.argmax(action_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Compute current Q values
        current_q = self.policy_net(states).gather(1, actions)
        
        # Compute target Q values
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.steps_done += 1
        if self.steps_done % self.update_frequency == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# --- Training Loop for DQN with Hyperparameter Search ---
if __name__ == "__main__":
    # Setup logger to store print statements in dqn.txt as well as display them
    class Logger(object):
        def __init__(self, stream, file):
            self.stream = stream
            self.file = file

        def write(self, message):
            self.stream.write(message)
            self.file.write(message)

        def flush(self):
            self.stream.flush()
            self.file.flush()

    log_file = open("dqn.txt", "w")
    sys.stdout = Logger(sys.stdout, log_file)

    total_start = time.time()  # Start timer for entire execution

    # Define hyperparameter search space
    config = {
        'grid_sizes': [10],
        'learning_rates': [1e-3],
        'discount_factors': [0.95],
        'epsilons': [0.05, 0.1, 0.2, 0.4, 0.5],
        'replay_buffer_sizes': [1e7],
        'max_steps_values': [10, 100, 1000, 10000, 100000],
        'batch_sizes': [32, 64, 128, 256],
        'update_frequencies': [1000],
        'episodes': 1000
    }
    
    best_results = {}
    best_params = {}
    overall_results = []

    for size in config['grid_sizes']:
        num_obstacles = max(5, size // 10)
        state_size = 4  # (robot_x, robot_y, dirt_x, dirt_y)
        action_size = 5
        
        for lr, gamma, eps, buffer_size, max_steps, batch_size, update_freq in product(
            config['learning_rates'],
            config['discount_factors'],
            config['epsilons'],
            config['replay_buffer_sizes'],
            config['max_steps_values'],
            config['batch_sizes'],
            config['update_frequencies']
        ):
            print(f"\nParams: grid_size={size}, lr={lr}, gamma={gamma}, epsilon={eps}, "
                  f"buffer_size={buffer_size}, max_steps={max_steps}, batch_size={batch_size}, update_freq={update_freq}")
            
            # Prepare config for the DQN agent
            dqn_config = {
                'lr': lr,
                'gamma': gamma,
                'epsilon': eps,
                'replay_buffer_size': buffer_size,
                'batch_size': batch_size,
                'update_frequency': update_freq,
                'epsilon_decay': 0.995
            }
            
            env = CleaningRobotEnv(size=size, num_obstacles=num_obstacles, max_steps=max_steps)
            agent = DQNAgent(state_size, action_size, dqn_config)
            rewards = []
            start_time_config = time.time()  # Timer for this configuration
            
            for ep in range(config['episodes']):
                state = env.reset_env()
                total_reward = 0
                done = False
                
                while not done:
                    action = agent.act(state)
                    next_state, reward, done, _ = env.step_env(action)
                    agent.remember(state, action, reward, next_state, done)
                    agent.replay()
                    state = next_state
                    total_reward += reward
                    
                    # Optionally render for small grids every 100 episodes
                    if ep % 100 == 0 and size <= 100:
                        env.render()
                
                rewards.append(total_reward)
                if ep % 100 == 0:
                    print(f"Episode {ep}, Total Reward: {total_reward}")
            
            time_taken_config = time.time() - start_time_config
            final_avg_reward = np.mean(rewards[-100:]) if len(rewards) >= 100 else np.mean(rewards)
            result_config = {
                'grid_size': size,
                'lr': lr,
                'gamma': gamma,
                'epsilon': eps,
                'replay_buffer_size': buffer_size,
                'max_steps': max_steps,
                'batch_size': batch_size,
                'update_freq': update_freq,
                'final_avg_reward': final_avg_reward,
                'time_taken': time_taken_config
            }
            overall_results.append(result_config)
            
            if size not in best_results or final_avg_reward > best_results[size]['final_avg_reward']:
                best_results[size] = {'final_avg_reward': final_avg_reward}
                best_params[size] = result_config
                os.makedirs("models/dqn", exist_ok=True)
                torch.save(agent.policy_net.state_dict(), f"models/dqn/best_model_{size}.pth")
    
    for size, params in best_params.items():
        print(f"\nBest params for grid size {size}:")
        for key, value in params.items():
            print(f"{key}: {value}")

    # Quit pygame if it was used
    if any(size <= 100 for size in config['grid_sizes']):
        pygame.quit()

    total_time = time.time() - total_start  # Total time for entire execution
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    # Close the log file
    log_file.close()
