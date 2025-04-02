# evaluation.py

import time
import numpy as np
from environment import RoomCleaningEnv
from q_learning import QLearningAgent
from dqn import DQNAgent

def evaluate_on_grid(grid_size, max_steps, num_obstacles):
    print(f"\nEvaluating on grid size: {grid_size}x{grid_size}")
    
    # Evaluate Q-Learning Agent
    try:
        env_q = RoomCleaningEnv(grid_size=grid_size, max_steps=max_steps, num_obstacles=num_obstacles)
        q_agent = QLearningAgent(env_q, alpha=0.1, gamma=0.9, epsilon=0.1, max_steps=max_steps)
        start_time = time.time()
        q_reward = q_agent.run_episode()
        q_time = time.time() - start_time
    except Exception as e:
        q_reward = None
        q_time = None
        print("Q-Learning failed on grid size", grid_size, ":", e)
    
    # Evaluate DQN Agent
    env_dqn = RoomCleaningEnv(grid_size=grid_size, max_steps=max_steps, num_obstacles=num_obstacles)
    dqn_agent = DQNAgent(env_dqn, lr=1e-3, gamma=0.9, epsilon=0.1,
                          replay_buffer_size=1e7, max_steps=max_steps,
                          batch_size=32, update_frequency=32*5)
    start_time = time.time()
    dqn_reward = dqn_agent.run_episode()
    dqn_time = time.time() - start_time
    
    print(f"Q-Learning: Reward = {q_reward}, Time = {q_time:.4f} sec" if q_reward is not None else "Q-Learning: Not evaluated")
    print(f"DQN:        Reward = {dqn_reward}, Time = {dqn_time:.4f} sec")
    
    return {
        "grid_size": grid_size,
        "q_reward": q_reward,
        "q_time": q_time,
        "dqn_reward": dqn_reward,
        "dqn_time": dqn_time
    }

def main_evaluation():
    # List of grid sizes (side lengths). Note: very large grids may be infeasible for Q-Learning.
    grid_sizes = [10, 100, 1000, 10000]  # You can extend this list as appropriate.
    max_steps = 100  # Maximum steps per episode.
    num_obstacles = 5  # Number of obstacles in the grid.
    
    results = []
    for size in grid_sizes:
        res = evaluate_on_grid(size, max_steps, num_obstacles)
        results.append(res)
    
    # Summarize results.
    print("\nSummary of Evaluation:")
    for res in results:
        print(f"Grid {res['grid_size']}x{res['grid_size']}: Q-Learning -> Reward: {res['q_reward']}, Time: {res['q_time']}, "
              f"DQN -> Reward: {res['dqn_reward']}, Time: {res['dqn_time']}")
    
    # Insights: For smaller grids, a Q-table is manageable and Q-Learning may learn a direct mapping.
    # As grid size increases, Q-Learning quickly becomes memory-intensive and slow.
    # DQN, by approximating the Q-values with a neural network, scales better to larger state spaces.
    # However, the training time per episode may increase with grid size, and the reward differences will
    # reflect both the exploration efficiency and the time penalty of moving in a larger environment.
    
if __name__ == '__main__':
    main_evaluation()