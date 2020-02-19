# Author    : Robert Geraghty
# Contact   : robertrgeraghty@gmail.com
# Date      : Feb 16, 2020

#branch test

import random
try:
    from CS5313_Localization_Env import maze
except:
    print('Problem finding CS5313_Localization_Env.maze... Trying to "import maze" only...')
    try:
        import maze
    except:
        print('Could not import maze')
from enum import Enum

class Directions(Enum):
    """An Enum containing the directions S, E, N, W, and St (stationary) and their respective (row, col) movement tuples. Ex. S = (1,0) meaning down one row, and stationary in the columns."""
    S = (1, 0)
    E = (0,1)
    N = (-1, 0)
    W = (0,-1)
    St = (0,0)

class Environment:
    """ An environment for testing a randomly moving robot around a maze.

    Important Class Variables\n
    map                     -- The map of the the maze. A 2d list of lists in the form map[row][column] where a value of 1 signifies there is a wall, 0 signifies the cell is traversable, and 'x' denotes the robot location.\n
    transistions_table      -- The table of transition probabilities for each cell. A 2d list of lists in the form map[row][column] where traversable cells contain a dictionary of Directions and Probabilities, and intraversable cells contain the value -1.\n
    robot_location          -- The current location of the robot, given as a tuple in the for (row, column).
    """
    def __init__(self, action_bias, observation_noise, action_noise, dimensions, seed = None):
        """Initializes the environment. The robot starts in a random traversable cell.
        
        Arguements:\n
        action_bias         -- Provides a bias for the robots actions. Positive values increase the likelihood of South and East movements, and negative favor North and West. (float in range -1-1)\n
        observation_noise   -- The probability that any given observation value will flip values erroneously. (float in range 0-1)\n
        action_noise        -- The probability that an action will move either direction perpendicular to the inteded direction. (float in range 0-1)\n
        dimensions          -- The dimensions of the map, given in the form (# of rows, # of columns). (tuple in range (1+, 1+))\n
        seed                -- The random seed value. (int)\n
        
        Return:\n
        No return
        """

        # save the bias, noise, and map sizze parameters
        self.action_bias = action_bias
        self.observation_noise = observation_noise
        self.action_noise = action_noise
        self.dimensions = dimensions

        # set the random seed and display it
        self.seed = seed if seed != None else random.randint(1, 10000)
        random.seed(self.seed)
        print("Random seed:", self.seed)

        # creat the map and list of free cells
        self.map = maze.make_maze(dimensions[0], dimensions[1], seed)
        self.free_cells = [(row, col) for row in range(dimensions[0]) for col in range(dimensions[1]) if self.map[row][col] == 0]
        
        # create the transistion table
        self.transitions_table = self.create_transitions_table()

        # set the robot location and print
        self.robot_location = self.free_cells[random.randint(0, len(self.free_cells)-1)]
        print("Robot starting location:", self.robot_location)
        self.map[self.robot_location[0]][self.robot_location[1]] = 'x'

        #####################################
        # Displaying can probably done here #
        #####################################
    
    def move(self):
        """Moves the robot to a new position based off of the transistion table and its current location.

        Return:\n
        A list of the observations modified by the observation noise, where 1 signifies a wall and 0 signifies an empty cell. The order of the list is [S, E, N, W]
        """
        # The the transition probabilities for the current robot location
        probs = self.transitions_table[self.robot_location[0]][self.robot_location[1]]
        sample = random.random() # take a random sample over interval [0,1)
        
        # loop through the directions and take the first action where the sum of transistion probabilities until that point is greater than the sample
        prob_sum = 0
        for direction in probs.keys():
            prob_sum += probs[direction]
            if prob_sum > sample:
                # Update the robot location
                self.map[self.robot_location[0]][self.robot_location[1]] = 0
                self.robot_location = (self.robot_location[0]+direction.value[0], self.robot_location[1]+direction.value[1])
                self.map[self.robot_location[0]][self.robot_location[1]] = 'x'
                break
        # return the new observation
        return self.observe()

    def observe(self):
        """Observes the walls at the current robot location

        Return:\n
        A list of the observations modified by the observation noise, where 1 signifies a wall and 0 signifies an empty cell. The order of the list is [S, E, N, W]
        """
        # get the neighboring walls to create the true observation table
        observations = [0 if self.traversable(self.robot_location[0], self.robot_location[1], direction) else 1 for direction in Directions if direction != Directions.St]
        # apply observation noise
        observations = [1-x if random.random() < self.observation_noise else x for x in observations]
        return observations

    def create_transitions_table(self):
        """Creates the transistion table for the map.

        Return:\n
        The table of transition probabilities for each cell. A 2d list of lists in the form map[row][column] where traversable cells contain a dictionary of Directions and Probabilities, and intraversable cells contain the value -1.\n
        """
        temp = []
        # loop through the rows
        for row in range(self.dimensions[0]):
            temp.append([])
            # loop through the columns
            for col in range(self.dimensions[1]):
                # If the cell is not traversable than set its value in the transition table to -1
                if self.map[row][col] == 1:
                    temp[row].append(-1)
                    continue

                probs = {}
                action_probs = {}
                
                # count the number of SE and NW traversable cells. Used later when computing action probabilities
                # se_count = 0
                # nw_count = 0
                # for d in [Directions.S, Directions.E]:
                #     if self.traversable(row, col, d):
                #         se_count += 1
                # for d in [Directions.N, Directions.W]:
                #     if self.traversable(row, col, d):
                #         nw_count += 1
                # total_count = se_count+nw_count

                # Compute Action Probabilities, accounting for walls, without noise
                # for key in Directions:
                #     if key in [Directions.S, Directions.E]: # Compute SE action probabilities
                #         if self.traversable(row, col, key): # if the cell is traversable set the probability otherwise set it to 0
                #             action_probs[key] = 1/total_count + self.action_bias/se_count
                #         else:
                #             action_probs[key] = 0
                #     elif key == Directions.St: # set stationary probability to 0, Robot can never try to stay still
                #         action_probs[key] = 0
                #     elif self.traversable(row,col,key): # Compute NW action probabilities
                #         action_probs[key] = 1/total_count - self.action_bias/nw_count
                #     else:
                #         action_probs[key] = 0
                
                # Compute Action Probabilities, without accounting for walls, without noise
                for key in Directions:
                    if key in [Directions.S, Directions.E]: # Compute SE action probabilities
                            action_probs[key] = 0.25 + self.action_bias/2
                    elif key == Directions.St: # set stationary probability to 0, Robot can never try to stay still
                        action_probs[key] = 0
                    else: # Compute NW action probabilities
                        action_probs[key] = 0.25 - self.action_bias/2
                    
               
                # normalize action probabilities
                action_sum = sum([action_probs[x] for x in Directions])
                
                for d in Directions:
                    action_probs[d] /= action_sum

                # Compute Transistion probabilities ignoring walls
                for direction in Directions:
                    probs[direction] = action_probs[direction] * (1-self.action_noise) # the base probabilty for each direction given action noise
                    if direction in [Directions.S, Directions.E]: # if the direction is SE then look at the action probabilities for NW to account for their action noise
                        for direction2 in [Directions.N, Directions.W]:
                            probs[direction] += action_probs[direction2]*(self.action_noise/2)
                    elif direction in [Directions.N, Directions.W]: # do the same as was done for SE but now for NW
                        for direction2 in [Directions.S, Directions.E]:
                            probs[direction] += action_probs[direction2]*(self.action_noise/2)
                probs[Directions.St] = 0    # init stationary probability

                # account for walls. If there is a wall for one of the transition probabilities add the probability to the stationary probability and set the transisition probability to 0
                for direction in Directions:
                    if not self.traversable(row, col, direction):
                        probs[Directions.St] += probs[direction]
                        probs[direction] = 0

                # add the new transistion probabilities
                temp[row].append(probs)
        return temp

                    

    def traversable(self, row, col, direction):
        """
        Returns true if the cell to the given direction of (row,col) is traversable, otherwise returns false.

        Arguements:\n
        row         -- the row of the initial cell\n
        col         -- the column of the initial cell\n
        direction   -- the direction of the cell to check for traversablility. Type: localization_env.Direction enum\n

        Return:\n
        A boolean signifying whether the cell to the given direction is traversable or not
        """
        # see if the cell in the direction is traversable. If statement to handle out of bounds errors
        if row+direction.value[0] >= 0 and row+direction.value[0] < self.dimensions[0] and col+direction.value[0] >= 0 and col+direction.value[0] < self.dimensions[1]:
            if self.map[row+direction.value[0]][col+direction.value[1]] == 0:
                return True
        return False

if __name__ == "__main__":
    Environment(.1,.1,.1,(10,10), seed=10)       

