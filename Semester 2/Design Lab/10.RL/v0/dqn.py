# dqn.py

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from environment import RoomCleaningEnv

# Neural network approximating Q-values.
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    
    def forward(self, x):
        return self.fc(x)

# Experience replay buffer.
class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = int(capacity)
        self.buffer = deque(maxlen=self.capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.array, zip(*batch))
        return state, action, reward, next_state, done
    
    def __len__(self):
        return len(self.buffer)

class DQNAgent:
    def __init__(self, env, lr, gamma, epsilon, replay_buffer_size, max_steps, batch_size, update_frequency,
                 epsilon_decay=0.995, epsilon_min=0.01):
        """
        DQN agent with epsilon decay.
        
        Parameters:
          - lr: Learning rate.
          - gamma: Discount factor.
          - epsilon: Initial exploration rate.
          - replay_buffer_size: Capacity of the replay buffer.
          - max_steps: Maximum steps per episode.
          - batch_size: Batch size for optimization.
          - update_frequency: Frequency (in steps) to update target network.
          - epsilon_decay: Multiplicative decay factor for epsilon.
          - epsilon_min: Minimum exploration rate.
        """
        self.env = env
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon  # initial epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.max_steps = max_steps
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_dim = 3  # (agent_x, agent_y, dirt_cleaned)
        self.output_dim = env.action_space.n
        
        self.policy_net = DQN(self.input_dim, self.output_dim).to(self.device)
        self.target_net = DQN(self.input_dim, self.output_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        
        self.replay_buffer = ReplayBuffer(replay_buffer_size)
        self.steps_done = 0
    
    def select_action(self, state):
        """Epsilon-greedy action selection with decay."""
        if random.random() < self.epsilon:
            action = self.env.action_space.sample()
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_vals = self.policy_net(state_tensor)
            action = int(torch.argmax(q_vals, dim=1).item())
        return action
    
    def optimize_model(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        current_q = self.policy_net(states).gather(1, actions)
        max_next_q = self.target_net(next_states).detach().max(1)[0].unsqueeze(1)
        expected_q = rewards + self.gamma * max_next_q * (1 - dones)
        
        loss = nn.MSELoss()(current_q, expected_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def run_episode(self):
        """Run one episode (with training) and return total reward."""
        state = self.env.reset()
        state = np.array(state, dtype=np.float32)
        total_reward = 0
        done = False
        steps = 0
        while not done and steps < self.max_steps:
            action = self.select_action(state)
            next_state, reward, done, _ = self.env.step(action)
            next_state = np.array(next_state, dtype=np.float32)
            self.replay_buffer.push(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            self.optimize_model()
            self.steps_done += 1
            if self.steps_done % self.update_frequency == 0:
                self.target_net.load_state_dict(self.policy_net.state_dict())
            steps += 1
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
        return total_reward

if __name__ == '__main__':
    # Quick demo for DQN
    env = RoomCleaningEnv(grid_size=10, max_steps=100, num_obstacles=5)
    agent = DQNAgent(env, lr=1e-3, gamma=0.9, epsilon=0.1,
                     replay_buffer_size=1e7, max_steps=100, batch_size=32, update_frequency=32*5)
    print("Episode Reward (DQN):", agent.run_episode())