# q_learning.py

import numpy as np
from environment import RoomCleaningEnv

class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1, max_steps=100):
        """
        Initializes the Q-learning agent.

        Parameters:
          - env: RoomCleaningEnv environment.
          - alpha: Learning rate.
          - gamma: Discount factor.
          - epsilon: Exploration rate.
          - max_steps: Maximum steps per episode.
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.max_steps = max_steps

        # Q-table shape: grid_size x grid_size x 2 (dirt_cleaned flag) x action_space size.
        self.q_table = np.zeros((env.grid_size, env.grid_size, 2, env.action_space.n))
    
    def choose_action(self, state):
        """Selects an action using an epsilon-greedy policy."""
        if np.random.rand() < self.epsilon:
            return self.env.action_space.sample()  # Exploration
        else:
            x, y, dirt_cleaned = state
            return np.argmax(self.q_table[x, y, dirt_cleaned])  # Exploitation
    
    def update_q_table(self, state, action, reward, next_state):
        """Update rule for Q-learning."""
        x, y, dirt_cleaned = state
        nx, ny, next_dirt_cleaned = next_state
        best_next = np.max(self.q_table[nx, ny, next_dirt_cleaned])
        self.q_table[x, y, dirt_cleaned, action] += self.alpha * (reward + self.gamma * best_next - self.q_table[x, y, dirt_cleaned, action])
    
    def train(self, episodes=500):
        """Train the agent for a given number of episodes."""
        rewards_per_episode = []
        for episode in range(episodes):
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
            rewards_per_episode.append(total_reward)
        return rewards_per_episode

def hyperparameter_search():
    # Hyperparameter ranges
    learning_rates = [0.1, 0.2, 0.5]
    discount_factors = [0.8, 0.9, 0.99]
    exploration_rates = [0.05, 0.1, 0.2, 0.4, 0.5]
    max_steps_options = [10, 100, 1000, 10000, 100000]

    env = RoomCleaningEnv(grid_size=10, max_steps=100)
    best_params = None
    best_avg_reward = float('-inf')
    
    for alpha in learning_rates:
        for gamma in discount_factors:
            for epsilon in exploration_rates:
                for max_steps in max_steps_options:
                    agent = QLearningAgent(env, alpha=alpha, gamma=gamma, epsilon=epsilon, max_steps=max_steps)
                    rewards = agent.train(episodes=500)
                    avg_reward = np.mean(rewards[-50:])  # average over last 50 episodes
                    print(f"α={alpha}, γ={gamma}, ε={epsilon}, Max Steps={max_steps}, Avg Reward={avg_reward}")
                    if avg_reward > best_avg_reward:
                        best_avg_reward = avg_reward
                        best_params = (alpha, gamma, epsilon, max_steps)
    
    print(f"\nBest Hyperparameters: α={best_params[0]}, γ={best_params[1]}, ε={best_params[2]}, Max Steps={best_params[3]}")
    return best_params, best_avg_reward

if __name__ == '__main__':
    best_params, best_avg_reward = hyperparameter_search()
    print("Hyperparameter search complete.")
