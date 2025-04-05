import numpy as np
import pygame
import time
from collections import defaultdict
from tqdm import tqdm
import argparse
import random
import os
from itertools import product

# ---------------------------
# Global Variables
# ---------------------------
q_table = defaultdict(lambda: np.zeros(5))

# ---------------------------
# Environment Functions
# ---------------------------

def init_environment(size, num_obstacles, num_dirts, visualize=False, delay=0.05):
    env = {
        'size': size,
        'num_dirts': num_dirts,
        'grid': np.zeros((size, size), dtype=np.uint8),
        'visualize': visualize,
        'delay': delay,
        'current_action': None,
        'current_reward': 0,
        'step_count': 0,
        'robot_pos': None,
        'dirt_positions': []
    }
    place_obstacles(env, num_obstacles)
    place_dirts(env)
    reset_environment(env)
    setup_visualization(env)
    return env

def place_obstacles(env, num_obstacles):
    size = env['size']
    grid = env['grid']
    grid[0, :] = grid[-1, :] = 1
    grid[:, 0] = grid[:, -1] = 1
    obstacles_placed = 0
    while obstacles_placed < num_obstacles:
        x, y = np.random.randint(1, size - 1, size=2)
        if grid[x, y] == 0:
            grid[x, y] = 1
            obstacles_placed += 1

def place_dirts(env):
    grid = env['grid']
    size = env['size']
    num_dirts = env['num_dirts']
    wall_positions = np.argwhere(grid == 1)
    candidates = []
    for wall_x, wall_y in wall_positions:
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            x, y = wall_x + dx, wall_y + dy
            if 0 <= x < size and 0 <= y < size and grid[x, y] == 0:
                candidates.append((x, y))
    if not candidates:
        candidates = [(x, y) for x in range(size) for y in range(size) if grid[x, y] == 0]
    weights = [1/(min(abs(x-wx) + abs(y-wy) for wx, wy in wall_positions)+1) for x, y in candidates]
    weights = np.array(weights)
    weights /= weights.sum()
    selected = np.random.choice(len(candidates), size=min(num_dirts, len(candidates)), replace=False, p=weights)
    env['dirt_positions'] = [candidates[i] for i in selected]
    for x, y in env['dirt_positions']:
        grid[x, y] = 2

def reset_environment(env):
    for x, y in env['dirt_positions']:
        env['grid'][x, y] = 0
    env['dirt_positions'] = []
    place_dirts(env)
    size = env['size']
    while True:
        x, y = np.random.randint(1, size - 1, size=2)
        if env['grid'][x, y] == 0 and (x, y) not in env['dirt_positions']:
            wall_adjacent = any(env['grid'][x+dx, y+dy] == 1 for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)])
            if not wall_adjacent:
                env['robot_pos'] = (x, y)
                break
    env['current_action'] = None
    env['current_reward'] = 0
    env['step_count'] = 0
    return get_state(env)

def get_state(env):
    x, y = env['robot_pos']
    return (x, y, tuple(sorted(env['dirt_positions'])))

def step_environment(env, action):
    x, y = env['robot_pos']
    reward = -1
    done = False
    if action < 4:
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][action]
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < env['size'] and 0 <= new_y < env['size'] and env['grid'][new_x, new_y] != 1:
            env['robot_pos'] = (new_x, new_y)
        else:
            reward = -5
    elif action == 4:
        if env['robot_pos'] in env['dirt_positions']:
            env['dirt_positions'].remove(env['robot_pos'])
            env['grid'][env['robot_pos']] = 0
            reward = 100
            if not env['dirt_positions']:
                done = True
        else:
            reward = -5
    env['current_action'] = action
    env['current_reward'] = reward
    env['step_count'] += 1
    return get_state(env), reward, done, {}

def setup_visualization(env):
    if env['visualize'] and env['size'] <= 100:
        pygame.init()
        cell_size = min(800 // env['size'], 40)
        screen_size = env['size'] * cell_size
        screen_height = screen_size + 40
        screen = pygame.display.set_mode((screen_size, screen_height))
        pygame.display.set_caption("Multi-Dirt Cleaning Robot")
        env.update({
            'cell_size': cell_size,
            'screen_size': screen_size,
            'screen_height': screen_height,
            'screen': screen,
            'clock': pygame.time.Clock(),
            'colors': {
                'bg': (30, 30, 30),
                'grid': (80, 80, 80),
                'wall': (70, 70, 70),
                'dirt': (255, 165, 0),
                'robot': (0, 200, 200)
            },
            'font': pygame.font.SysFont("Arial", 20)
        })
    else:
        env['screen'] = None

def render_environment(env):
    if not env['visualize'] or env['screen'] is None:
        return
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
    screen = env['screen']
    cell_size = env['cell_size']
    screen.fill(env['colors']['bg'])
    for i in range(env['size']):
        for j in range(env['size']):
            rect = pygame.Rect(j*cell_size, i*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, env['colors']['grid'], rect, 1)
            if env['grid'][i, j] == 1:
                pygame.draw.rect(screen, env['colors']['wall'], rect)
            elif (i, j) in env['dirt_positions']:
                pygame.draw.rect(screen, env['colors']['dirt'], rect)
    center = (env['robot_pos'][1]*cell_size + cell_size//2, env['robot_pos'][0]*cell_size + cell_size//2)
    pygame.draw.circle(screen, env['colors']['robot'], center, cell_size//2 - 2)
    info_panel = pygame.Surface((env['screen_size'], 40), pygame.SRCALPHA)
    info_panel.fill((0, 0, 0, 150))
    action_names = ['Left', 'Down', 'Right', 'Up', 'Clean']
    info_text = f"Action: {action_names[env['current_action']] if env['current_action'] is not None else 'None'} | "
    info_text += f"Reward: {env['current_reward']} | Step: {env['step_count']} | Dirt left: {len(env['dirt_positions'])}"
    text_surface = env['font'].render(info_text, True, (0, 0, 0))
    info_panel.blit(text_surface, (10, 10))
    screen.blit(info_panel, (0, env['screen_size']))
    pygame.display.flip()
    env['clock'].tick(30)
    time.sleep(env['delay'])

# ---------------------------
# Q-learning Functions
# ---------------------------

def choose_action(state, env, epsilon):
    if np.random.random() < epsilon:
        return np.random.randint(5)
    rx, ry, dirt = state
    if (rx, ry) in dirt:
        return 4
    if dirt:
        nearest = min(dirt, key=lambda d: abs(rx - d[0]) + abs(ry - d[1]))
        dx = nearest[0] - rx
        dy = nearest[1] - ry
        if abs(dx) > abs(dy):
            action = 1 if dx > 0 else 3
        else:
            action = 2 if dy > 0 else 0
        nx = rx + (1 if action == 1 else -1 if action == 3 else 0)
        ny = ry + (1 if action == 2 else -1 if action == 0 else 0)
        if 0 <= nx < env['size'] and 0 <= ny < env['size'] and env['grid'][nx, ny] != 1:
            return action
    return np.argmax(q_table[state])

def update_q_table(state, action, reward, next_state, alpha, gamma):
    current_q = q_table[state][action]
    max_next = np.max(q_table[next_state])
    q_table[state][action] += alpha * (reward + gamma * max_next - current_q)

# ---------------------------
# Main Execution
# ---------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=10)
    parser.add_argument('--dirts', type=int, default=3)
    parser.add_argument('--visualize', action='store_true')
    args = parser.parse_args()

    env = init_environment(args.size, num_obstacles=5, num_dirts=args.dirts, visualize=args.visualize)
    print(f"\nTraining on {args.size}x{args.size} grid with {args.dirts} dirt cells...")
    rewards = []
    alpha, gamma, epsilon = 0.1, 0.99, 0.1
    for ep in tqdm(range(1000), desc="Training"):
        state = reset_environment(env)
        total_reward = 0
        eps = epsilon * (0.99 ** ep)
        for _ in range(100):
            action = choose_action(state, env, eps)
            next_state, reward, done, _ = step_environment(env, action)
            update_q_table(state, action, reward, next_state, alpha, gamma)
            total_reward += reward
            state = next_state
            if ep % 50 == 0 and env['visualize']:
                render_environment(env)
            if done:
                break
        rewards.append(total_reward)
    print("\nTraining complete!")
    print(f"Average reward (last 100 episodes): {np.mean(rewards[-100:]):.2f}")
    print(f"Maximum reward: {np.max(rewards)}")
    print(f"Minimum reward: {np.min(rewards)}")
    if env['visualize']:
        pygame.quit()

if __name__ == '__main__':
    main()