# Sources and Attribution

This file records the external projects studied or adapted during the development of **Bloxorz AI Lab** and distinguishes them from the work implemented by the project team.

## 1. Primary baseline: EIACD Roll the Block

- Repository: `https://github.com/PedroNJorge/roll-the-block`
- Author: Pedro Jorge
- Copyright: 2025
- License: MIT
- Local license copy: `LICENSE`

The project began from the general structure of this repository. The reused or adapted baseline included:

- the initial Python/Pygame application organization;
- the board and block abstractions;
- the basic renderer and menu structure;
- the initial level representation;
- the initial organization of search modules;
- introductory implementations or concepts related to BFS, DFS, IDS, UCS, Greedy Search, and A*.

The current project substantially modified and extended this baseline. Because the submitted source still contains material derived from the MIT-licensed project, the original copyright and permission notice are preserved in `LICENSE` and `NOTICE.md`.

## 2. Study reference: Erroler/Bloxorz

- Repository: `https://github.com/Erroler/Bloxorz`

This repository was consulted only as a study reference for:

- JSON-based level organization;
- menu and interaction ideas;
- presentation of algorithm comparisons;
- organization of larger puzzle-level collections.

No ownership is claimed over material from this repository. Its source should not be copied or substantially adapted unless its license and reuse conditions are independently verified.

## 3. Study reference: Bloxorz Solver

- Repository: `https://gitlab.com/egealpay/bloxorz-solver`
- Author: Ege Alpay
- Copyright: 2018
- License: MIT

This project was studied for:

- UCS and A* organization;
- priority-queue usage;
- solver structure;
- ideas for presenting search results.

Any source copied or substantially adapted from this MIT-licensed project must retain the applicable copyright and permission notice.

## 4. Project-team contributions

The project team independently implemented or substantially redesigned the following components:

- immutable and hashable `GameState`;
- one shared state representation for manual play and all search algorithms;
- deterministic bridge-state representation;
- persistent one-time-switch state through `used_switches`;
- transition-based search interface;
- repeated-state handling based on complete game states;
- validation and handling of advanced tile types;
- soft, heavy, toggle, and permanent switch behavior;
- split-switch activation and cube teleportation;
- independent split-cube control and active-cube switching;
- automatic rejoining of adjacent split cubes;
- solver support for bridge and split states;
- unified `SearchResult` metrics;
- search-time, peak-memory, expanded-node, solution-length, and path-cost reporting;
- comparison mode for BFS, DFS, UCS, and A*;
- replay support for each solved comparison algorithm;
- CSV export from the comparison screen;
- non-uniform fragile-tile cost for UCS and A*;
- relaxed-graph heuristic for A* with split-switch teleport edges;
- JSON level loading and validation;
- modern isometric 2.5D rendering;
- pause and resume controls for AI playback;
- revised menus, legends, popups, and block proportions.

## 5. Development tools and AI assistance

The project was developed using:

- Python 3.12;
- Pygame;
- Git and GitHub;
- Visual Studio Code.

Generative AI assistance was used for planning, concept explanation, debugging suggestions, refactoring ideas, test design, documentation drafting, and code review support.

The project team remained responsible for:

- selecting and integrating accepted changes;
- reviewing source-code compatibility;
- executing the program;
- checking algorithm behavior;
- validating gameplay manually;
- collecting experimental results;
- writing the final report and conclusions;
- preserving third-party attribution and license notices.

AI-generated suggestions were not treated as automatically correct and were accepted only after review and local verification.
