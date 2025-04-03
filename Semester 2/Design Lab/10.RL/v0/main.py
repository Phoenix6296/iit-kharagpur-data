# main.py

import matplotlib.pyplot as plt
from environment import RoomCleaningEnv
from dqn import DQNAgent, dqn_hyperparameter_search

def main():
    # Run DQN hyperparameter search
    best_params, _ = dqn_hyperparameter_search()
    
    # Unpack best hyperparameters:
    lr, gamma, epsilon, max_steps, batch_size, update_frequency = best_params
    print("\nTraining DQN Agent with best hyperparameters...")
    
    # Create the environment
    env = RoomCleaningEnv(grid_size=10, max_steps=100)
    
    # Initialize DQN agent with best hyperparameters
    agent = DQNAgent(env, lr=lr, gamma=gamma, epsilon=epsilon,
                     replay_buffer_size=1e7, max_steps=max_steps,
                     batch_size=batch_size, update_frequency=update_frequency)
    
    # Train the agent for more episodes (e.g., 500 episodes)
    episode_rewards = agent.train(num_episodes=500)
    
    # Plot the training progress
    plt.plot(episode_rewards)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("DQN Training Rewards")
    plt.show()
    
    # Demonstrate one episode with visual rendering
    state = env.reset()
    done = False
    while not done:
        action = agent.select_action(state)
        state, reward, done, _ = env.step(action)
        env.render_visual(action=action, reward=reward, pause_time=0.5)
    
    print("Demo episode finished.")

if __name__ == '__main__':
    main()