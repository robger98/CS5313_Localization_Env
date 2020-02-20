# Author    : Robert Geraghty
# Contact   : robertrgeraghty@gmail.com
# Date      : Feb 16, 2020

import random

try:
    from CS5313_Localization_Env import maze
except:
    print(
        'Problem finding CS5313_Localization_Env.maze... Trying to "import maze" only...'
    )
    try:
        import maze

        print("Successfully imported maze")
    except:
        print("Could not import maze")
from enum import Enum


# Change this to true to print out information on the robot location and heading
printouts = True
# Change this to true inorder to print out the map as a dataframe to console every time move() is called, as well as the Transition Tables to csv files named "heading.csv" and "location.csv". Won't do anything if printouts is false expect import pandas
df = True
if df:
    from pandas import DataFrame


class Directions(Enum):
    """An Enum containing the directions S, E, N, W, and St (stationary) and their respective (row, col) movement tuples. Ex. S = (1,0) meaning down one row, and stationary in the columns."""

    S = (1, 0)
    E = (0, 1)
    N = (-1, 0)
    W = (0, -1)
    St = (0, 0)

    def get_ortho(self, value):
        """ Return the Direction Enums orthogonal to the given direction

        Arguements:\n
        value           -- The given direction for which the orthogonal directions will be based on.\n

        Returns:\n
        A list of directions orthogonal to the given direction.
        """
        if value in [self.N, self.S]:
            return [self.W, self.E]
        return [self.N, self.S]


class Headings(Enum):
    """An enum containing the headings S, E, N, W and their respective (row, col) movement tuples"""

    S = (1, 0)
    E = (0, 1)
    N = (-1, 0)
    W = (0, -1)

    def get_ortho(self, value):
        """ Return the Headings Enums orthogonal to the given heading

        Arguements:\n
        value           -- The given heading for which the orthogonal heading will be based on.\n

        Returns:\n
        A list of headings orthogonal to the given heading.
        """
        if value in [self.N, self.S]:
            return [self.W, self.E]
        return [self.N, self.S]


class Environment:
    """ An environment for testing a randomly moving robot around a maze.

    Important Class Variables\n
    map                     -- The map of the the maze. A 2d list of lists in the form map[row][column] where a value of 1 signifies there is a wall, 0 signifies the cell is traversable, and 'x' denotes the robot location.\n
    location_transition     -- The table of transition probabilities for each cell. Format is [row][col][heading][direction] which will return the probabilities of moving the direction, given the robot's current row, column, and heading.\n
    heading_transitions     -- The table of transition probabilities for the headings given each cell. Format is [row][col][heading][heading] which will return the probabilities of each heading for the next time step given the robot's current row, col, and heading.\n
    robot_location          -- The current location of the robot, given as a tuple in the for (row, column).
    robot_heading           -- The current heading of the robot, given as a Headings enum.
    """

    def __init__(
        self, action_bias, observation_noise, action_noise, dimensions, seed=None
    ):
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

        # creat the map and list of free cells
        self.map = maze.make_maze(dimensions[0], dimensions[1], seed)
        self.free_cells = [
            (row, col)
            for row in range(dimensions[0])
            for col in range(dimensions[1])
            if self.map[row][col] == 0
        ]

        # create the transistion table
        self.location_transitions = self.create_locations_table()
        self.headings_transitions = self.create_headings_table()

        if df:
            DataFrame(self.location_transitions).to_csv("location.csv")
            DataFrame(self.headings_transitions).to_csv("heading.csv")

        # set the robot location and print
        self.robot_location = self.free_cells[
            random.randint(0, len(self.free_cells) - 1)
        ]

        self.map[self.robot_location[0]][self.robot_location[1]] = "x"

        # Set the robot heading
        self.robot_heading = random.choice(
            [
                h
                for h in Headings
                if self.traversable(self.robot_location[0], self.robot_location[1], h)
            ]
        )

        if printouts:
            print("Random seed:", self.seed)
            print("Robot starting location:", self.robot_location)
            print("Robot starting heading:", self.robot_heading)

            if df:
                print(DataFrame(self.map))

    def random_dictionary_sample(self, probs):
        sample = random.random()
        prob_sum = 0
        for key in probs.keys():
            prob_sum += probs[key]
            if prob_sum > sample:
                return key

    def move(self):
        """Updates the robots heading and moves the robot to a new position based off of the transistion table and its current location and new heading.

        Return:\n
        A list of the observations modified by the observation noise, where 1 signifies a wall and 0 signifies an empty cell. The order of the list is [S, E, N, W]
        """

        # Get the new heading
        h_probs = self.headings_transitions[self.robot_location[0]][
            self.robot_location[1]
        ][self.robot_heading]
        self.robot_heading = self.random_dictionary_sample(h_probs)

        # get the new location
        self.map[self.robot_location[0]][self.robot_location[1]] = 0
        probs = self.location_transitions[self.robot_location[0]][
            self.robot_location[1]
        ][self.robot_heading]

        direction = self.random_dictionary_sample(probs)

        self.robot_location = (
            self.robot_location[0] + direction.value[0],
            self.robot_location[1] + direction.value[1],
        )
        self.map[self.robot_location[0]][self.robot_location[1]] = "x"

        # return the new observation
        if printouts:
            print()
            print(self.robot_heading)
            print(direction)
            if df:
                print(DataFrame(self.map))
        return self.observe()

    def observe(self):
        """Observes the walls at the current robot location

        Return:\n
        A list of the observations modified by the observation noise, where 1 signifies a wall and 0 signifies an empty cell. The order of the list is [S, E, N, W]
        """
        # get the neighboring walls to create the true observation table
        observations = [
            0
            if self.traversable(
                self.robot_location[0], self.robot_location[1], direction
            )
            else 1
            for direction in Directions
            if direction != Directions.St
        ]
        # apply observation noise
        observations = [
            1 - x if random.random() < self.observation_noise else x
            for x in observations
        ]
        return observations

    def create_locations_table(self):
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
                temp[row].append({})
                for heading in list(Headings):
                    probs = {}

                    # Compute Transistion probabilities ignoring walls
                    for direction in Directions:
                        if direction.name == heading.name:
                            probs[direction] = 1 - self.action_noise
                        elif direction in Directions.get_ortho(
                            Directions, Directions[heading.name]
                        ):
                            probs[direction] = self.action_noise / 2
                        else:
                            probs[direction] = 0
                        # init stationary probability
                        probs[Directions.St] = 0

                        # account for walls. If there is a wall for one of the transition probabilities add the probability to the stationary probability and set the transisition probability to 0
                    for direction in Directions:
                        if not self.traversable(row, col, direction):
                            probs[Directions.St] += probs[direction]
                            probs[direction] = 0

                    # add the new transistion probabilities
                    temp[row][col].update({heading: probs})
        return temp

    def create_headings_table(self):
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
                temp[row].append({})

                for heading in Headings:
                    probs = {}
                    # Handle case when the current heading is traversable
                    if self.traversable(row, col, heading):
                        for new_heading in Headings:
                            if heading == new_heading:
                                probs[new_heading] = 1
                            else:
                                probs[new_heading] = 0
                        temp[row][col].update({heading: probs})
                        continue

                    # If the current heading is not traversable

                    # Find which headings are available
                    headings_traversablity = {}
                    for new_heading in Headings:
                        if self.traversable(row, col, new_heading):
                            headings_traversablity[new_heading] = 1
                        else:
                            headings_traversablity[new_heading] = 0

                    # Sum these values for later arithmetic
                    total_traversable = sum(list(headings_traversablity.values()))
                    se_traversable = (
                        headings_traversablity[Headings.S]
                        + headings_traversablity[Headings.E]
                    )
                    nw_traversable = (
                        headings_traversablity[Headings.N]
                        + headings_traversablity[Headings.W]
                    )

                    # Compute the heading probabilities for traversable headings
                    for new_heading in Headings:
                        if self.traversable(row, col, new_heading):
                            if new_heading in [Headings.S, Headings.E]:
                                probs[new_heading] = (
                                    1 / total_traversable
                                    + self.action_bias / se_traversable
                                )

                            else:
                                probs[new_heading] = (
                                    1 / total_traversable
                                    - self.action_bias / nw_traversable
                                )
                        else:
                            probs[new_heading] = 0

                    # normalize heading probabilities
                    probs_sum = sum([probs[x] for x in Headings])
                    for h in Headings:
                        probs[h] /= probs_sum

                    # add the new transistion probabilities
                    temp[row][col].update({heading: probs})
        return temp

    def traversable(self, row, col, direction):
        """
        Returns true if the cell to the given direction of (row,col) is traversable, otherwise returns false.

        Arguements:\n
        row         -- the row of the initial cell\n
        col         -- the column of the initial cell\n
        direction   -- the direction of the cell to check for traversablility. Type: localization_env.Directions enum or localization_env.Headings\n

        Return:\n
        A boolean signifying whether the cell to the given direction is traversable or not
        """
        # see if the cell in the direction is traversable. If statement to handle out of bounds errors
        if (
            row + direction.value[0] >= 0
            and row + direction.value[0] < self.dimensions[0]
            and col + direction.value[0] >= 0
            and col + direction.value[0] < self.dimensions[1]
        ):
            if self.map[row + direction.value[0]][col + direction.value[1]] == 0:
                return True
        return False


if __name__ == "__main__":
    env = Environment(0.1, 0.1, 0.1, (10, 10), seed=10)
    print("Starting test. Press <enter> to make move")
    while True:
        env.move()
        input()
