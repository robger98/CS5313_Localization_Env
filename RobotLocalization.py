"""
    Skeleton Code for Visualization by James Hale
"""

import localization_env as Le
import pygame
import random
import numpy as np


def _init_pygame(window_size):
    pygame.init()
    pygame.display.set_caption("ROBOT MAP")
    return pygame.display.set_mode(window_size), pygame.time.Clock()


def update(screen, window_size, env_map, robot_loc, prob_map, heading_probs=[1, 1, 1, 1]):
    x_dir = window_size[0]/len(env_map[0])
    y_dir = window_size[0]/len(env_map)
    screen.fill((0, 0, 0))
    a = np.argmax(prob_map)
    most_prob = [a//len(prob_map[0]), a%len(prob_map[0])]
    for i in range(len(env_map)):
        for j in range(len(env_map[i])):
            if env_map[i][j] == 1:
                color = (0, 0, 0)
            elif i == most_prob[0] and j == most_prob[1]:
                color = (218, 165, 32)
            else:
                color = ((1-prob_map[i][j])*255, (1-prob_map[i][j]*.2)* 255, (1-prob_map[i][j]*.2)* 255)
            pygame.draw.rect(screen, color, [i*x_dir, j*y_dir, x_dir, y_dir])
        pygame.draw.circle(screen, (255, 100, 100), (int(robot_loc[0]*x_dir)+int(x_dir/2), int(robot_loc[1]*y_dir)+
                                                 int(y_dir/2)), int(x_dir/2.5))
    # Draw lines
    for i in range(len(heading_probs)):
        if i == 0: # DOWN
            pygame.draw.line(screen, (0,0,0),  (int(robot_loc[0]*x_dir)+int(x_dir/2), int(robot_loc[1]*y_dir)+
                                                 int(y_dir/2)),  (int(robot_loc[0]*x_dir)+int(x_dir/2), int(robot_loc[1]*y_dir)+
                                                 int(y_dir/2) + heading_probs[i]*y_dir/2.5))
        elif i == 1: # UP
            pygame.draw.line(screen, (0, 0, 0), (int(robot_loc[0] * x_dir) + int(x_dir / 2), int(robot_loc[1] * y_dir) +
                                                 int(y_dir / 2)),
                             (int(robot_loc[0] * x_dir) + int(x_dir / 2), int(robot_loc[1] * y_dir) +
                              int(y_dir / 2) - heading_probs[i] * y_dir / 2.5))
        elif i == 2: # Right
            pygame.draw.line(screen, (0, 0, 0), (int(robot_loc[0] * x_dir) + int(x_dir / 2), int(robot_loc[1] * y_dir) +
                                                 int(y_dir / 2)),
                             (int(robot_loc[0] * x_dir) + int(x_dir / 2) + heading_probs[i] * x_dir / 2.5, int(robot_loc[1] * y_dir) +
                              int(y_dir / 2)))
        else: # LEFT
            pygame.draw.line(screen, (0, 0, 0), (int(robot_loc[0] * x_dir) + int(x_dir / 2), int(robot_loc[1] * y_dir) +
                                                 int(y_dir / 2)),
                             (int(robot_loc[0] * x_dir) + int(x_dir / 2) - heading_probs[i] * x_dir / 2.5,
                              int(robot_loc[1] * y_dir) +
                              int(y_dir / 2)))


def generate_possibilities(env):
    # JUST A SAMPLE PROBABILITY MAP, YOU'll GENERATE YOUR OWN AT EACH ITERATION
    prob_map = list()
    for i in env.map:
        a = list()
        for j in i:
            if j != 1:
                a.append(random.uniform(0, 1))
            else:
                a.append(0)
        prob_map.append(a)
    ###
    return prob_map


def main():
    seed = 100
    speed = 1  # The higher, the lower
    random.seed(seed)
    window_size = [750, 750]
    env = Le.Environment(.1, .1, .1, (10, 10), seed=seed)
    screen, clock = _init_pygame(window_size)
    done = False
    i = 0
    while not done:
        if i == 100:
            i = 0
        if i % speed == 0:
            env.move()
            update(screen, window_size, env.map, env.robot_location, generate_possibilities(env),
                   heading_probs=np.random.rand(4))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        clock.tick(60)
        pygame.display.flip()
        i += 1


if __name__ == '__main__':
    main()