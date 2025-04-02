# q_learning.py

import numpy as np
from environment import RoomCleaningEnv

class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1, max_steps=100):
        """
        Q-Learning agent.
        Q-table dimensions: grid_size x grid_size x 2 x action_space size.
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.max_steps = max_steps
        
        self.q_table = np.zeros((env.grid_size, env.grid_size, 2, env.action_space.n))
    
    def choose_action(self, state):
        """Epsilon-greedy policy."""
        if np.random.rand() < self.epsilon:
            return self.env.action_space.sample()
        else:
            x, y, dirt_cleaned = state
            return np.argmax(self.q_table[x, y, dirt_cleaned])
    
    def update_q_table(self, state, action, reward, next_state):
        x, y, dirt_cleaned = state
        nx, ny, next_dirt_cleaned = next_state
        best_next = np.max(self.q_table[nx, ny, next_dirt_cleaned])
        self.q_table[x, y, dirt_cleaned, action] += self.alpha * (
            reward + self.gamma * best_next - self.q_table[x, y, dirt_cleaned, action]
        )
    
    def run_episode(self):
        """Run one episode (without training) and return total reward."""
        state = self.env.reset()
        total_reward = 0
        done = False
        steps = 0
        while not done and steps < self.max_steps:
            action = self.choose_action(state)
            next_state, reward, done, _ = self.env.step(action)
            self.update_q_table(state, action, reward, next_state)
            state = next_state
            total_reward += reward
            steps += 1
        return total_reward

if __name__ == '__main__':
    # Quick demo
    env = RoomCleaningEnv(grid_size=10, max_steps=100, num_obstacles=5)
    agent = QLearningAgent(env)
    print("Episode Reward (Q-Learning):", agent.run_episode())
