# EIACD-Roll-the-Block

## Introduction
This project recreates the classic Bloxorz puzzle game (without the teleport feature) and implements various search algorithms to automatically solve each level, i.e. **Breath-First Search**, **Depth-First Search**, **Iterative Deepening Search**, **Uniform-Cost Search**, for the uninformed search algorithms, and, **Greedy Search**, **A\* Search**, for the informed search algorithms. Bloxorz is a 3D block-rolling puzzle game where players navigate a rectangular block through challenging terrain to reach a goal hole.

## Project Structure

```
.
├── environment.yml                      # Conda environment configuration
├── game/                                # Core game implementation
│   ├── __init__.py                      # Makes 'game' a package
│   ├── block.py                         # Block physics and state management
│   ├── board.py                         # Game board
│   ├── game_logic.py                    # Main game rules and state transitions
│   ├── input_handler.py                 # User input processing
│   ├── levels.py                        # Level definitions and parsing
│   └── renderer.py                      # Visualization and graphics
├── search_algorithms/                   # AI solvers
│   ├── __init__.py                      # Makes 'search_algorithms' a package
│   ├── a_star.py                        # A* search implementation
│   ├── breadth_first_search.py          # Breadth-first search implementation
│   ├── depth_first_search.py            # Depth-first search implementation
│   ├── expand.py                        # Function responsible to expand nodes
│   ├── greedy_search.py                 # Greedy search implementation
│   ├── heuristic.py                     # Heuristic Function
│   ├── iterative_deepening_search.py    # Iterative deepening search implementation
│   ├── node.py                          # Node Class
│   ├── problem.py                       # Problem Class
│   └── uniform_cost_search.py           # Uniform-Cost search implementation
│
├── main.py                              # Entry point
├── LICENSE                              # MIT License
└── README.md                            # This documentation
├── Time_Memory_Statistics.ods           # Statistics about each search algorithm
├── Roll_the_Block_checkpoint.pdf        # Chekpoint presented
└── Roll_the_Block_final.pdf             # Final Presentation
```

## Game Rules
The game features a 2x1x1 rectangular block that can move in four direction: **up**, **down**, **right**, **left**.
1. **Block States**:
   - **Upright** (2 cubes stacked in the z-axis)
   - **Horizontal** (2 cubes side by side in the x-axis)
   - **Vertical** (2 cubes side by side in the y-axis
  
<div align="center">

|Upright|Horizontal|Vertical|
|-|-|-|
| ![Alt1](https://github.com/user-attachments/assets/2ea5e162-915a-4098-86b0-59b527e1b5da) | ![Alt2](https://github.com/user-attachments/assets/9c52ab50-6608-48c8-ab20-5d31e0707092) | ![Alt3](https://github.com/user-attachments/assets/6b428657-d946-4903-8bdc-c4ae601ce78e) |

</div>

2. **Level Elements**:
   - **Void tiles**: The block falls over, ending the game
   - **Floor tiles**: Can support the block in any orientation
   - **Glass Floor tiles**: Break if the block stands upright on them (must be crossed lying flat)
   - **Goal tile**: The hole where the block must end in the upright state to win
   - **Hidden Path**: Require the block to activate switches to cross
   - **Buttons**
     * *X Type*: Require the block to be standing upright to activate
     * *Hexagonal Type*: Can be activated by the block in any orientation
     * *One-Time-Use Type*: Have the same visual cue as the X Type, but only function one time

3. **Movement**:
   - The block always rolls over an edge
   - Each move changes the block's orientation
   - From the upright state, any roll makes the block lay flat (horizontal/vertical)
   - From the horizontal/vertical state, rolling "forward" makes it stand up, while rolling "sideways" keeps it flat

4. **Losing Conditions**:
   - Block falls off the map (touches a void tile)
   - Block stands upright on a glass tile

## Project Features
- Faithful recreation of the original Bloxorz game mechanics
- Visual representation of the game board and block movement
- Multiple implemented search algorithms to solve puzzles automatically
- Implementation of the *Manhattan distance* as an heuristic for the informed search algorithms
- Step-by-step solution visualization given by the chosen search algorithm
Matrix Caption: </br>
* `-2` - Hidden Path
* `-1` - Void
* `0` - Floor
* `1` - Block "upright"
* `2` - Block "horizontal" / "vertical"
* `3` - Glass Floor
* `4` - X Type Button
* `5` - Hexagonal Type Button
* `6` - One Time Use Type Button
* `7` - Goal

## Implementation Details
The project is implemented in Python3 and features:
- Modular game logic separated from algorithm implementations
- Clean object-oriented design for game elements
- Visualization layer to observe the solving process
- Performance metrics for algorithm comparison

```bash
# Installation (using conda)
git clone https://github.com/PedroNJorge/EIACD-Roll-the-Block
cd EIACD-Roll-the-Block
conda create -f environment.yml
```

## How to Use
1. Run the main file to launch the game:
   ```bash
   conda activate environment
   python3 main.py
   ```
2. Play manually using the WASD or arrow keys
3. Or select a search algorithm from the menu
4. View solution statistics and replay solutions

## Acknowledgments
Inspired by the original Bloxorz game by Damien Clarke, released on August 22, 2007. This project was created for educational purposes to explore search algorithms in game AI.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
