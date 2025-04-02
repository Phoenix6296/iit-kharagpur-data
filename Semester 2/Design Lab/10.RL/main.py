# main.py

import matplotlib.pyplot as plt
from environment import RoomCleaningEnv
from q_learning import QLearningAgent, hyperparameter_search

def main():
    # Run hyperparameter search
    best_params, _ = hyperparameter_search()
    
    # Create environment with chosen hyperparameters for visualization demonstration.
    env = RoomCleaningEnv(grid_size=10, max_steps=100)
    agent = QLearningAgent(env, alpha=best_params[0], gamma=best_params[1], epsilon=best_params[2], max_steps=best_params[3])
    
    # Train agent for demonstration
    episodes = 500
    rewards = agent.train(episodes=episodes)
    
    # Plot training rewards
    plt.plot(rewards)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Training Rewards Over Episodes")
    plt.show()
    
    # Demonstrate one episode with visual rendering.
    state = env.reset()
    done = False
    while not done:
        action = agent.choose_action(state)
        state, reward, done, _ = env.step(action)
        env.render_visual(action=action, reward=reward, pause_time=0.5)
    
    print("Demo episode finished.")

if __name__ == '__main__':
    main()