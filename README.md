# Bloxorz AI Lab

A Python/Pygame implementation of the Bloxorz puzzle with manual play, advanced tiles, split-cube mechanics, multiple search algorithms, performance measurement, and an isometric 2.5D interface.

> Repository: `https://github.com/tuhuynhhhh/Project1_Bloxorz`

## Highlights

- Manual play with WASD or arrow keys
- New Game, Restart, Pause/Resume AI, and algorithm-selection controls
- Isometric 2.5D board and block rendering
- Fragile tiles, bridges, soft switches, heavy switches, permanent/one-time switches, and split switches
- Split-cube control with `Space` and automatic rejoining
- BFS, DFS, IDS, UCS, Greedy Search, and A*
- Unified immutable `GameState` shared by all solvers
- Search metrics: time, peak memory, expanded nodes, solution length, and total cost
- Run All comparison screen and CSV export
- JSON level format with validation and Python fallback
- Automated tests for movement, transitions, advanced tiles, split mechanics, solvers, metrics, benchmark export, UCS cost, and A* heuristic

## Screenshots

Add the final screenshots to `screenshots/` and keep these names:

```text
screenshots/main_menu.png
screenshots/human_mode.png
screenshots/ai_mode.png
screenshots/split_level.png
screenshots/comparison_table.png
screenshots/level_complete.png
```

Example:

```markdown
![Main menu](screenshots/main_menu.png)
```

## Requirements

- Windows 10/11, Linux, or macOS
- Python 3.12 recommended
- Pygame 2.6.1

## Installation on Windows

Clone the repository:

```bat
git clone https://github.com/tuhuynhhhh/Project1_Bloxorz.git
cd Project1_Bloxorz
```

Create and activate a virtual environment:

```bat
py -m venv .venv
.venv\Scripts\activate
```

Upgrade pip and install dependencies:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the game:

```bat
python main.py
```

## Controls

| Input | Action |
|---|---|
| `W` / Up arrow | Move up |
| `S` / Down arrow | Move down |
| `A` / Left arrow | Move left |
| `D` / Right arrow | Move right |
| `Space` | Switch the active cube while split |
| Mouse | Select menus, levels, algorithms, Pause/Resume, Restart, and New Game |

## Game rules

The normal block occupies two unit cubes and has three orientations:

- `upright`: one board cell, height two
- `horizontal`: two adjacent cells in one axis
- `vertical`: two adjacent cells in the other axis

The level is solved only when the normal block is upright on the goal.

### Tile codes

| Code | Tile | Behavior |
|---:|---|---|
| `-2` | Closed bridge / hidden path | Acts as void until opened |
| `-1` | Void | The block falls |
| `0` | Floor | Supports every valid orientation |
| `3` | Fragile tile | Supports a lying block or single split cube, but not an upright normal block |
| `4` | Heavy switch | Activated only by an upright normal block |
| `5` | Soft switch | Activated by any occupied block part, including a single split cube |
| `6` | Permanent/one-time heavy switch | Activated once by an upright normal block |
| `7` | Goal | Requires an upright normal block |
| `8` | Split switch | Requires an upright normal block and teleports it into two cubes |

### Split mechanics

A split switch converts the normal `1x1x2` block into two independent `1x1x1` cubes. Only one cube moves at a time. Press `Space` to change the active cube. Adjacent cubes automatically rejoin into the normal block. A single cube can activate a soft switch, but cannot activate a heavy switch or complete the level.

## Search algorithms

| Algorithm | Type | Notes |
|---|---|---|
| BFS | Uninformed | Finds the minimum number of actions under unit depth |
| DFS | Uninformed | Memory-efficient but not optimal |
| IDS | Uninformed | Combines DFS memory with increasing depth limits |
| UCS | Cost-based | Uses the accumulated transition cost |
| Greedy | Informed | Uses only the heuristic |
| A* | Informed | Uses `f(n) = g(n) + h(n)` |

### Cost model

The final UCS/A* configuration uses:

- normal roll or split-cube switch: cost `1`
- successor state occupying a fragile tile: cost `3`

This makes UCS meaningfully different from BFS while preserving positive action costs.

### A* heuristic

The heuristic uses a relaxed graph:

- ignores block orientation and fragile restrictions
- treats closed bridge positions as traversable in the relaxation
- includes split-switch teleport edges
- computes point distance to the goal
- divides by two because one normal roll can advance an occupied cell by at most two grid edges
- adds a safe lower bound when the state is not upright

See `docs/ARCHITECTURE.md` and `report/REPORT_DRAFT.md`.

## Level files

Levels are stored in:

```text
levels/level1.json
...
levels/level10.json
```

The same parsed level is used by manual play and every solver. The embedded Python level dictionary remains as a fallback.

See `docs/LEVEL_FORMAT.md`.

## Run tests

Run the complete suite:

```bat
python -m unittest discover -s tests -p "test_*.py" -v
```

Run a specific file:

```bat
python -m unittest discover -s tests -p "test_advanced_tiles.py" -v
```

The final release should record the exact passing test count in `docs/REQUIREMENTS_AUDIT.md`.

## Benchmark

Core algorithms on representative levels:

```bat
python benchmark.py ^
  --levels LEVEL1 LEVEL2 LEVEL4 LEVEL6 LEVEL9 LEVEL10 ^
  --algorithms BFS UCS "A*" ^
  --repeats 5 ^
  --output benchmark_results\final_core.csv
```

Run DFS separately to avoid long runs on difficult levels:

```bat
python benchmark.py ^
  --levels LEVEL1 LEVEL2 ^
  --algorithms DFS ^
  --repeats 5 ^
  --output benchmark_results\final_dfs.csv
```

Summarize results and generate charts:

```bat
python -m pip install -r requirements-report.txt
python tools\summarize_benchmark.py ^
  --input benchmark_results\final_core.csv benchmark_results\final_dfs.csv ^
  --output-dir benchmark_results\final
```

## Project structure

```text
.
├── game/                       # Game state, rules, levels, rendering, input
├── levels/                     # Shared JSON level data
├── search_algorithms/          # BFS, DFS, IDS, UCS, Greedy, A*
├── tests/                      # Automated test suite
├── tools/                      # Benchmark summary and release packaging
├── benchmark_results/          # Final CSV files and charts
├── docs/                       # Architecture, audit, attribution, AI usage
├── report/                     # Report draft and final PDF
├── screenshots/                # Images used by README/report
├── benchmark.py
├── main.py
├── requirements.txt
├── requirements-report.txt
├── SOURCES.md
├── NOTICE.md
└── README.md
```

## Clean release package

Create a source-only ZIP without `.git`, `.venv`, caches, backup files, or cloned references:

```bat
python tools\package_release.py
```

The package is created inside `dist/`.

## Publishing all work to GitHub

See `docs/GITHUB_PUBLISH.md`. Push the main branch, feature branches, and tags to preserve the complete project history.

## Report and video

- Draft: `report/REPORT_DRAFT.md`
- Final report: `report/Report.pdf`
- Demo video URL: place it in `report/video_link.txt` and in the final report

## Attribution

This project began from the MIT-licensed `roll-the-block` project by Pedro Jorge and was substantially redesigned. Other repositories were studied for ideas. Exact attribution, licenses, and original contributions are documented in `SOURCES.md` and `NOTICE.md`.

## License

The existing MIT license and upstream copyright notice must remain in the repository because substantial portions originated from the MIT-licensed baseline.
