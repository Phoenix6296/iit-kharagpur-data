import pygame
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

# Initialize Pygame right at the start
pygame.init()

# --- DQN Network ---
class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# --- Environment Class ---
class CleaningRobotEnv:
    def __init__(self, size=10, num_dirt=3):
        self.size = size
        self.num_dirt = num_dirt
        self.cell_size = 40
        self.screen_size = self.size * self.cell_size
        self.screen_height = self.screen_size + 40  # Add space for info panel
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_height))
        pygame.display.set_caption("Cleaning Robot DQN")
        
        # Visualization parameters from CODE2
        self.bg_color = (30, 30, 30)
        self.grid_color = (80, 80, 80)
        self.wall_color = (70, 70, 70)
        self.dirt_color = (255, 165, 0)
        self.robot_color = (0, 200, 200)
        self.font = pygame.font.SysFont("Arial", 20)
        
        # Tracking variables for visualization
        self.current_action = None
        self.current_reward = 0
        self.step_count = 0
        
        self.reset()

    def reset(self):
        self.grid = np.zeros((self.size, self.size))
        # Place border walls
        self.grid[0, :] = self.grid[-1, :] = 1
        self.grid[:, 0] = self.grid[:, -1] = 1
        # Place dirt
        self.dirt_positions = []
        for _ in range(self.num_dirt):
            while True:
                x, y = np.random.randint(1, self.size-1, 2)
                if self.grid[x, y] == 0:
                    self.grid[x, y] = 2
                    self.dirt_positions.append((x, y))
                    break
        # Place robot
        while True:
            x, y = np.random.randint(1, self.size-1, 2)
            if self.grid[x, y] == 0:
                self.robot_pos = (x, y)
                break
        
        # Reset tracking variables
        self.current_action = None
        self.current_reward = 0
        self.step_count = 0
        return self._get_state()

    def step(self, action):
        x, y = self.robot_pos
        reward = -1
        done = False

        # Update tracking variables for visualization
        self.current_action = action
        self.step_count += 1

        # Movement actions
        if action < 4:
            dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][action]
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size and self.grid[new_x, new_y] != 1:
                self.robot_pos = (new_x, new_y)
        
        # Clean action
        elif action == 4:
            if (x, y) in self.dirt_positions:
                reward = 100
                self.dirt_positions.remove((x, y))
                self.grid[x, y] = 0

        # Check if done
        if len(self.dirt_positions) == 0:
            done = True
            reward = 200  # Bonus for completing

        # Update current reward for visualization
        self.current_reward = reward
        return self._get_state(), reward, done, {}

    def _get_state(self):
        state = np.copy(self.grid)
        state[self.robot_pos] = 3
        return state.flatten()

    def render(self):
        # Main grid drawing
        self.screen.fill(self.bg_color)
        
        # Draw grid cells
        for x in range(self.size):
            for y in range(self.size):
                rect = pygame.Rect(y*self.cell_size, x*self.cell_size, 
                                  self.cell_size, self.cell_size)
                # Draw grid borders
                pygame.draw.rect(self.screen, self.grid_color, rect, 1)
                
                # Draw obstacles
                if self.grid[x, y] == 1:
                    pygame.draw.rect(self.screen, self.wall_color, rect)
                
                # Draw dirt
                if (x, y) in self.dirt_positions:
                    pygame.draw.rect(self.screen, self.dirt_color, rect)

        # Draw robot
        robot_center = (self.robot_pos[1]*self.cell_size + self.cell_size//2,
                        self.robot_pos[0]*self.cell_size + self.cell_size//2)
        radius = self.cell_size//2 - 2
        pygame.draw.circle(self.screen, self.robot_color, robot_center, radius)

        # Draw info panel (CODE2 style)
        info_panel = pygame.Surface((self.screen_size, 40), pygame.SRCALPHA)
        info_panel.fill((0, 0, 0, 150))
        action_names = ['Up', 'Right', 'Down', 'Left', 'Clean']
        info_text = (f"Action: {action_names[self.current_action] if self.current_action is not None else 'None'} | "
                    f"Reward: {self.current_reward} | Step: {self.step_count}")
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        info_panel.blit(text_surface, (10, 10))
        self.screen.blit(info_panel, (0, self.screen_size))

        pygame.display.flip()

# --- Training Loop ---
def train_dqn(env, episodes=5):
    input_size = env.size * env.size
    output_size = 5  # 4 movements + clean
    
    policy_net = DQN(input_size, output_size)
    target_net = DQN(input_size, output_size)
    target_net.load_state_dict(policy_net.state_dict())
    optimizer = optim.Adam(policy_net.parameters(), lr=0.001)
    buffer = ReplayBuffer(10000)
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Epsilon-greedy action
            epsilon = max(0.1, 1.0 - episode / episodes)
            if random.random() < epsilon:
                action = random.randint(0, 4)
            else:
                with torch.no_grad():
                    q_values = policy_net(torch.FloatTensor(state).unsqueeze(0))
                action = q_values.argmax().item()
            
            # Environment step
            next_state, reward, done, _ = env.step(action)
            buffer.push(state, action, reward, next_state, done)
            total_reward += reward
            state = next_state
            
            # Render every step
            env.render()
            # pygame.time.delay(50)  # Slow down for visualization
            
            # Train on batch
            if len(buffer) >= 128:
                batch = buffer.sample(128)
                states = torch.FloatTensor([x[0] for x in batch])
                actions = torch.LongTensor([x[1] for x in batch])
                rewards = torch.FloatTensor([x[2] for x in batch])
                next_states = torch.FloatTensor([x[3] for x in batch])
                dones = torch.FloatTensor([x[4] for x in batch])
                
                current_q = policy_net(states).gather(1, actions.unsqueeze(1))
                next_q = target_net(next_states).max(1)[0].detach()
                target_q = rewards + 0.99 * next_q * (1 - dones)
                
                loss = nn.MSELoss()(current_q.squeeze(), target_q)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        
        # Update target network
        if episode % 10 == 0:
            target_net.load_state_dict(policy_net.state_dict())
        
        print(f"Episode {episode}, Total Reward: {total_reward}")

# --- Experience Replay ---
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

# --- Main Execution ---
if __name__ == "__main__":
    env = CleaningRobotEnv(size=10, num_dirt=3)
    train_dqn(env)
    pygame.quit()