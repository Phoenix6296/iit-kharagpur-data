import numpy as np
import argparse
import pygame
import time
from tqdm import tqdm

# ---------------------------
# Pygame-based Environment Functions
# ---------------------------
def create_cleaning_environment(grid_size=10, obstacle_count=5, show_visuals=False, update_delay=0.1):
    environment = {}
    environment['grid_size'] = grid_size
    environment['grid'] = np.zeros((grid_size, grid_size), dtype=np.uint8)
    environment['grid'][0, :] = environment['grid'][-1, :] = 1
    environment['grid'][:, 0] = environment['grid'][:, -1] = 1
    obstacles_placed = 0
    while obstacles_placed < obstacle_count:
        x, y = np.random.randint(1, grid_size - 1, size=2)
        if environment['grid'][x, y] == 0:
            environment['grid'][x, y] = 1
            obstacles_placed += 1

    environment['dirt_position'] = None
    place_dirt_near_walls(environment)
    reset_environment(environment)

    environment['show_visuals'] = show_visuals
    if grid_size <= 100 and show_visuals:
        pygame.init()
        cell_dimension = min(800 // grid_size, 40)
        environment['cell_dimension'] = cell_dimension
        environment['screen_size'] = grid_size * cell_dimension
        environment['screen_height'] = environment['screen_size'] + 40
        environment['screen'] = pygame.display.set_mode((environment['screen_size'], environment['screen_height']), pygame.DOUBLEBUF)
        pygame.display.set_caption("Cleaning Robot")
        environment['clock'] = pygame.time.Clock()
        environment['bg_color'] = (30, 30, 30)
        environment['grid_color'] = (80, 80, 80)
        environment['wall_color'] = (70, 70, 70)
        environment['dirt_color'] = (255, 165, 0)
        environment['robot_color'] = (0, 200, 200)
        environment['font'] = pygame.font.SysFont("Arial", 20)
        environment['pygame'] = pygame
        environment['update_delay'] = update_delay
    else:
        environment['screen'] = None
        environment['pygame'] = None
    return environment

def place_dirt_near_walls(environment):
    grid_size = environment['grid_size']
    grid = environment['grid']
    candidates = []
    wall_positions = np.argwhere(grid == 1)
    for (wx, wy) in wall_positions:
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            x, y = wx + dx, wy + dy
            if 0 <= x < grid_size and 0 <= y < grid_size and grid[x, y] == 0:
                candidates.append((x, y))
    if not candidates:
        candidates = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x, y] == 0]
    if candidates:
        weights = []
        for (x, y) in candidates:
            min_dist = min(abs(x - wx) + abs(y - wy) for (wx, wy) in wall_positions)
            weights.append(1 / (min_dist + 1))
        weights = np.array(weights)
        weights /= weights.sum()
        idx = np.random.choice(len(candidates), p=weights)
        environment['dirt_position'] = candidates[idx]
        environment['grid'][environment['dirt_position']] = 2

def reset_environment(environment):
    grid_size = environment['grid_size']
    grid = environment['grid']
    while True:
        x, y = np.random.randint(1, grid_size - 1, size=2)
        if grid[x, y] == 0 and (x, y) != environment['dirt_position']:
            wall_adjacent = False
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                if grid[x + dx, y + dy] == 1:
                    wall_adjacent = True
                    break
            if not wall_adjacent:
                environment['robot_position'] = (x, y)
                break
    environment['current_action'] = None
    environment['current_reward'] = 0
    environment['step_count'] = 0
    return np.array([environment['robot_position'][0], environment['robot_position'][1],
                     environment['dirt_position'][0], environment['dirt_position'][1]], dtype=np.int32)

def step_in_environment(environment, action):
    x, y = environment['robot_position']
    reward = -1
    done = False
    grid_size = environment['grid_size']

    if action < 4:
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        dx, dy = moves[action]
        new_x, new_y = x + dx, y + dy
        # Check collision with walls or obstacles
        if new_x < 0 or new_x >= grid_size or new_y < 0 or new_y >= grid_size or environment['grid'][new_x, new_y] == 1:
            new_x, new_y = x, y
        environment['robot_position'] = (new_x, new_y)
    elif action == 4:
        if environment['robot_position'] == environment['dirt_position']:
            reward = 100
            done = True
            environment['grid'][environment['dirt_position']] = 0  # Remove the dirt
        else:
            reward = -5

    environment['current_action'] = action
    environment['current_reward'] = reward
    environment['step_count'] += 1
    state = np.array([environment['robot_position'][0], environment['robot_position'][1],
                      environment['dirt_position'][0], environment['dirt_position'][1]], dtype=np.int32)
    return state, reward, done, {}

def render_environment(environment):
    if environment['screen'] is None:
        return
    pygame = environment['pygame']
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
    environment['screen'].fill(environment['bg_color'])
    grid_size = environment['grid_size']
    cell_dimension = environment['cell_dimension']
    # Draw grid and cells
    for i in range(grid_size):
        for j in range(grid_size):
            rect = pygame.Rect(j * cell_dimension, i * cell_dimension, cell_dimension, cell_dimension)
            pygame.draw.rect(environment['screen'], environment['grid_color'], rect, 1)
            if environment['grid'][i, j] == 1:
                pygame.draw.rect(environment['screen'], environment['wall_color'], rect)
            elif (i, j) == environment['dirt_position']:
                pygame.draw.rect(environment['screen'], environment['dirt_color'], rect)
    # Draw robot
    robot_x, robot_y = environment['robot_position']
    robot_center = (robot_y * cell_dimension + cell_dimension // 2, robot_x * cell_dimension + cell_dimension // 2)
    radius = cell_dimension // 2 - 2
    pygame.draw.circle(environment['screen'], environment['robot_color'], robot_center, radius)
    # Draw info panel
    info_panel = pygame.Surface((environment['screen_size'], 40), pygame.SRCALPHA)
    info_panel.fill((0, 0, 0, 150))
    action_names = ['Up', 'Right', 'Down', 'Left', 'Clean']
    action_str = action_names[environment['current_action']] if environment['current_action'] is not None else 'None'
    info_text = f"Action: {action_str} | Reward: {environment['current_reward']} | Step: {environment['step_count']}"
    text_surface = environment['font'].render(info_text, True, (255, 255, 255))
    info_panel.blit(text_surface, (10, 10))
    environment['screen'].blit(info_panel, (0, environment['screen_size']))
    pygame.display.flip()
    environment['clock'].tick(30)
    time.sleep(environment['update_delay'])

# ---------------------------
# Q-Learning Agent Functions (adapted for 5 actions)
# ---------------------------
def select_action(state, environment, q_table, exploration_rate):
    robot_x, robot_y, dirt_x, dirt_y = state
    if robot_x == dirt_x and robot_y == dirt_y:
        return 4
    dx = dirt_x - robot_x
    dy = dirt_y - robot_y
    if abs(dx) > abs(dy):
        desired = 1 if dx > 0 else 3  # Right or Left
    else:
        desired = 2 if dy > 0 else 0  # Down or Up
    if np.random.random() < exploration_rate:
        return np.random.randint(5)
    q_values = [q_table.get((tuple(state), a), 0) for a in range(5)]
    return int(np.argmax(q_values))

def update_q_values(state, action, reward, next_state, q_table, learning_rate, discount_factor):
    """
    Update the Q-table using the Q-learning update rule.
    """
    old_q = q_table.get((tuple(state), action), 0)
    max_next_q = max([q_table.get((tuple(next_state), a), 0) for a in range(5)])
    q_table[(tuple(state), action)] = old_q + learning_rate * (reward + discount_factor * max_next_q - old_q)

def train_agent(environment, episodes=1000, max_steps=100, learning_rate=0.1, discount_factor=0.99,
                exploration_rate=0.1, render_interval=50):
    rewards_history = []
    q_table = {}
    for ep in tqdm(range(episodes), desc="Training Q-Learning"):
        state = reset_environment(environment)
        total_reward = 0
        for step in range(max_steps):
            action = select_action(state, environment, q_table, exploration_rate)
            next_state, reward, done, _ = step_in_environment(environment, action)
            if ep % render_interval == 0 and environment['show_visuals']:
                render_environment(environment)
            update_q_values(state, action, reward, next_state, q_table, learning_rate, discount_factor)
            total_reward += reward
            state = next_state
            if done:
                break
        rewards_history.append(total_reward)
        exploration_rate = max(0.01, exploration_rate * 0.995)
    return rewards_history, q_table

def perform_hyperparameter_search(environment):
    print("Starting quick hyperparameter search for Q-Learning...")
    candidate_learning_rates = [0.05, 0.1, 0.2]
    candidate_discount_factors = [0.9, 0.95, 0.99]
    candidate_exploration_rates = [0.05, 0.1, 0.2, 0.4, 0.5]
    candidate_max_steps = [10, 100, 1000, 10000, 100000]
    best_avg_reward = -np.inf
    best_params = None
    search_episodes = 50

    for lr in candidate_learning_rates:
        for df in candidate_discount_factors:
            for er in candidate_exploration_rates:
                for ms in candidate_max_steps:
                    reset_environment(environment)
                    rewards, _ = train_agent(environment, episodes=search_episodes, max_steps=ms,
                                             learning_rate=lr, discount_factor=df, exploration_rate=er, render_interval=search_episodes+1)
                    avg_reward = np.mean(rewards)
                    print(f"lr={lr}, df={df}, er={er}, max_steps={ms} -> Avg Reward: {avg_reward:.2f}")
                    if avg_reward > best_avg_reward:
                        best_avg_reward = avg_reward
                        best_params = {'learning_rate': lr, 'discount_factor': df, 'exploration_rate': er, 'max_steps': ms}
    print("Best hyperparameters:", best_params)
    return best_params

def evaluate_performance(hyperparam=False, show_visuals=False):
    grid_sizes = [10, 100, 1000]
    evaluation_results = {}
    for grid_size in grid_sizes:
        print(f"\nEvaluating grid size: {grid_size}x{grid_size}")
        environment = create_cleaning_environment(grid_size=grid_size, obstacle_count=5, show_visuals=show_visuals)
        if hyperparam:
            best_params = perform_hyperparameter_search(environment)
            max_steps = best_params['max_steps']
            learning_rate = best_params['learning_rate']
            discount_factor = best_params['discount_factor']
            exploration_rate = best_params['exploration_rate']
            print(f"Best params for grid size {grid_size}: {best_params}")
        else:
            max_steps = 100
            learning_rate = 0.1
            discount_factor = 0.99
            exploration_rate = 0.1
        start_time = time.time()
        rewards, q_table = train_agent(environment, episodes=10, max_steps=max_steps,
                                       learning_rate=learning_rate, discount_factor=discount_factor, exploration_rate=exploration_rate, render_interval=100)
        elapsed = time.time() - start_time
        evaluation_results[grid_size] = elapsed
        print(f"Time taken for grid size {grid_size}: {elapsed:.2f} seconds")
    return evaluation_results

# ---------------------------
# Main Function
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    # Only these flags are used: --hyperparameter, --visualize, and --evaluate
    parser.add_argument('--hyperparameter', action='store_true', help='Run hyperparameter tuning')
    parser.add_argument('--visualize', action='store_true', help='Visualize the environment using pygame')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation mode over multiple grid sizes')
    args = parser.parse_args()

    if args.evaluate:
        evaluation_results = evaluate_performance(hyperparam=args.hyperparameter, show_visuals=args.visualize)
        print("\nEvaluation Results (Grid Size : Time in sec):")
        for size, t in evaluation_results.items():
            print(f"{size} : {t:.2f} sec")
    else:
        # For non-evaluation training, use a default grid size (e.g., 10x10) and episodes (e.g., 1000)
        environment = create_cleaning_environment(grid_size=10, obstacle_count=5, show_visuals=args.visualize, update_delay=0.01)
        if args.hyperparameter:
            best_params = perform_hyperparameter_search(environment)
            rewards, q_table = train_agent(environment, episodes=1000,
                                           max_steps=best_params['max_steps'],
                                           learning_rate=best_params['learning_rate'],
                                           discount_factor=best_params['discount_factor'],
                                           exploration_rate=best_params['exploration_rate'],
                                           render_interval=1001)
        else:
            rewards, q_table = train_agent(environment, episodes=1000,
                                           max_steps=100, learning_rate=0.1, discount_factor=0.99, exploration_rate=0.1)
        print("\nTraining Completed.")
        print(f"Total Episodes: 1000")
        print(f"Final Episode Reward: {rewards[-1]}")
        print(f"Average Reward: {np.mean(rewards):.2f}")
        print(f"Min Reward: {np.min(rewards):.2f}")
        print(f"Max Reward: {np.max(rewards):.2f}")

if __name__ == "__main__":
    main()