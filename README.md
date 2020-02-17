# CS5313_Localization_Env

Localization environment for the second project of CS5313-SP20 - Advanced Artificial Intelligence

## Installation

Download the repository and add the whole folder "CS5313_Localization_Env" to your project as a subfolder.
In order to make use of the code, import it with

```python
from CS5313_Localization_Env import localization_env as Le
```

## Usage

First you must initialize an environment. This is done with:

```python
env = Le.Environment(action_bias, observation_noise, action_noise, dimensions, seed=seed)
```

where you supply the values for the arguments.

Then, in order to move your robot within the environment, it is as simple as:

```python
observation = env.move()
```

where `move()` returns the next observation.

Observations can also be retrieved with:

```python
observation = env.observe()
```

You can access every variable within the environment with the form:

```pyton
env.<variable_name>
```

## Directions Enum

The directions in this program are represented with an Enum Class called `Directions`. The transition table uses these to represent movements in each of the cardinal directions as well as a stationary move, which happens when action noise causes the robot to run into a wall. This class can be accessed with `Le.Directions` for interpreting the transition tables.

More can be learned by reading the comments in `localization_env.py`.

## Variables

The variables in the environment are as follows:

```text
action_bias       The supplied action bias, changing won't do anything
observation_bias  The supplied observation bias, changing wont do anything
action_noise      The supplied action noise, changing won't do anything
dimensions        The map dimensions, changing will BREAK the program
seed              The random seed, changing won't do anything
map               The map, changing will BREAK the program
free_cells        A list of traversable cells, changing won't do anything
transitions_table The transistion table for the cells, changing will BREAK the program
robot_location    The location of the robot, changing will BREAK the program
```

You shouldn't need to change any variables after initializing the enviroment, and doing so will either do nothing or break the program, so don't. 

More detailed descriptions of the variables, such as their type and format can be seen in the comments.

## Other Notes

The coordinate system used in this environment is (Row, Column), not (x, y). 

All the generated mazes are completely enclosed by walls. This is to prevent action noise from causing the robot to go out of bounds. I'm mainly mentioning this so if you edit the the maze generation code you make sure to leave the bounding walls.

## Support

If you find a bug please email me at rrg053@utulsa.edu or robertrgeraghty@gmail.com, as I don't generally check the class discussion board on harvey.
