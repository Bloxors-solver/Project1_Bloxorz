# Bloxorz AI Lab

Bloxorz AI Lab is a Python/Pygame implementation of the Bloxorz puzzle. The project supports manual play, advanced tiles, split-cube mechanics, classical search algorithms, performance metrics, solution replay, and an isometric 2.5D interface.

## Features

- Manual play with WASD or arrow keys
- Ten JSON levels
- Fragile tiles, bridges, soft switches, heavy switches, permanent switches, and split switches
- Independent control of split cubes with `Space`
- Automatic cube rejoining
- BFS, DFS, IDS, UCS, Greedy Search, and A*
- Search metrics: time, peak memory, expanded nodes, solution length, and total cost
- Comparison mode for BFS, DFS, UCS, and A*
- Replay for each solved comparison algorithm
- CSV export from comparison mode

## Requirements

- Python 3.12 recommended
- Pygame 2.6.1

Install all required packages from `requirements.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/Bloxors-solver/Project1_Bloxorz.git
cd Project1_Bloxorz
```

Create a virtual environment on Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the game

Run the command from the repository root:

```powershell
python main.py
```

Do not run individual files inside `game/` or `search_algorithms/`.

## Controls

| Input | Action |
|---|---|
| `W` / Up arrow | Move up |
| `S` / Down arrow | Move down |
| `A` / Left arrow | Move left |
| `D` / Right arrow | Move right |
| `Space` | Switch the active cube while split |
| Mouse | Select menus, levels, algorithms, replay, pause, restart, and new game |

## Search algorithms

| Algorithm | Description |
|---|---|
| BFS | Expands the shallowest nodes first |
| DFS | Expands the deepest available node first |
| IDS | Repeats depth-limited search with increasing limits |
| UCS | Expands the node with the lowest accumulated cost |
| Greedy | Uses only the heuristic estimate |
| A* | Uses accumulated cost plus heuristic estimate |

The project uses a positive non-uniform cost model:

- Normal movement or active-cube switching: cost `1`
- A successor occupying a fragile tile: cost `3`

## Project structure

```text
.
├── game/                 # Game rules, state, rendering, and input
├── levels/               # JSON level definitions
├── search_algorithms/    # Search algorithms and comparison logic
├── main.py               # Application entry point
├── requirements.txt      # Runtime dependencies
├── LICENSE               # Upstream MIT license
├── NOTICE.md             # Attribution notice
├── SOURCES.md            # Source and adaptation disclosure
└── README.md
```

The application creates `benchmark_results/` automatically when comparison results are exported to CSV.

## Attribution

This project began from the MIT-licensed `roll-the-block` project by Pedro Jorge and was substantially extended and redesigned. See `SOURCES.md`, `NOTICE.md`, and `LICENSE` for attribution and licensing details.
