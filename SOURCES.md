# Sources and attribution

This file documents external repositories, what was studied or reused, and the project team's original work.

## 1. Primary baseline: Roll the Block

- Repository: `https://github.com/PedroNJorge/roll-the-block`
- Original project title: EIACD Roll the Block
- Copyright: Pedro Jorge, 2025
- License: MIT
- Local license file: `LICENSE`

### Used or adapted

The project began from this repository's overall game structure, including:

- initial Pygame application organization
- board and block concepts
- menu/renderer baseline
- initial level representation
- initial search-module organization
- basic BFS, DFS, UCS, Greedy, IDS, and A* concepts

The MIT copyright and permission notice must remain in copies containing substantial portions of the original software.

## 2. Secondary study: Erroler/Bloxorz

- Repository: `https://github.com/Erroler/Bloxorz`
- Studied for:
  - JSON level organization
  - menu and interaction ideas
  - algorithm-comparison presentation
  - larger collections of puzzle levels

The local clone did not contain an obvious license file. Treat this repository as a study reference only unless its license/permission is independently confirmed. Do not copy unlicensed source code into the submitted project.

Its README also states that some algorithm code was adapted from the AIMA Python repository. This project does not claim ownership of that external work.

## 3. Secondary study: Bloxorz Solver

- Repository: `https://gitlab.com/egealpay/bloxorz-solver`
- Copyright: Ege Alpay, 2018
- License: MIT
- Studied for:
  - UCS and A* organization
  - priority-queue usage
  - solver/report ideas

Any copied or substantially adapted MIT-licensed material must retain its copyright and permission notice.

## 4. Original project contributions

The current project independently added or substantially redesigned:

- immutable and hashable `GameState`
- one shared state representation for manual play and all search algorithms
- deterministic bridge-state representation
- persistent `used_switches`
- transition-based search API
- safe repeated-state handling
- advanced-tile validation
- heavy, soft, toggle, and permanent/one-time switch behavior
- split switch, cube teleportation, active-cube switching, and automatic rejoining
- solver support for split and bridge states
- unified `SearchResult` metrics
- repeatable benchmark and CSV export
- Run All comparison screen
- A* replay from comparison results
- non-uniform fragile-tile cost for UCS and A*
- relaxed-graph A* heuristic with split-switch teleport edges
- JSON level loader and validation
- automated tests for movement, transitions, advanced tiles, solvers, metrics, benchmarks, costs, and heuristics
- modern isometric 2.5D interface
- pause/resume AI playback
- revised tile legend, menus, popups, and block proportions
- release/documentation workflow

## 5. Tools and assistance

Development tools included:

- Python 3.12
- Pygame
- Git and GitHub
- Visual Studio Code
- unittest
- ChatGPT for planning, debugging assistance, test design, documentation drafting, and code review suggestions

The team reviewed, integrated, executed, and tested all submitted code. See `docs/AI_USAGE.md`.
