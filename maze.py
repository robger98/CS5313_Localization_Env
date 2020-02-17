# Random Maze Generator using Depth-first Search
# http://en.wikipedia.org/wiki/Maze_generation_algorithm
# FB - 2012-12-14

# Code taken from http://code.activestate.com/recipes/578356-random-maze-generator/ used and modified under MIT license

import random
from pandas import DataFrame


def make_maze(row, col, seed):
    random.seed(seed)
    mx = col; my = row # width and height of the maze
    maze = [[1 for x in range(mx)] for y in range(my)]
    dx = [0, 1, 0, -1]; dy = [-1, 0, 1, 0] # 4 directions to move in the maze
    # start the maze from a random cell

    stack = [(random.randint(1, mx - 2), random.randint(1, my - 2))]
    while len(stack) > 0:
        (cx, cy) = stack[-1]
        maze[cy][cx] = 0
        # find a new cell to add
        nlst = [] # list of available neighbors
        for i in range(4):
            nx = cx + dx[i]; ny = cy + dy[i]
            if nx >= 1 and nx < mx-1 and ny >= 1 and ny < my-1:
                if maze[ny][nx] == 1:
                    # of occupied neighbors must be 1
                    ctr = 0
                    for j in range(4):
                        ex = nx + dx[j]; ey = ny + dy[j]
                        if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                            if maze[ey][ex] == 0: ctr += 1
                    if ctr == 1: nlst.append(i)
        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            ir = nlst[random.randint(0, len(nlst) - 1)]
            cx += dx[ir]; cy += dy[ir]
            stack.append((cx, cy))
        else: stack.pop()
    return maze
