# Bloxorz AI Search Project Report

> Replace every bracketed placeholder before submission.

## Cover page

- Course: `[Course name]`
- Project: Bloxorz AI Search
- Class: `[Class]`
- Instructor: `[Instructor]`
- Students:
  - `[Student ID] — [Full name]`
  - `[Student ID] — [Full name]`
- Repository: `https://github.com/tuhuynhhhh/Project1_Bloxorz`
- Demo video: `[YouTube URL]`
- Date: `[Submission date]`

## 1. Introduction

Bloxorz is a deterministic puzzle in which a `1x1x2` rectangular block rolls across a finite board. The objective is to place the block upright on the goal without falling into void cells or violating tile constraints. The problem is suitable for classical state-space search because each legal action produces a deterministic successor state and the board contains a finite number of configurations.

This project implements manual play and multiple search algorithms in Python. It also supports advanced mechanics: fragile tiles, bridges, soft and heavy switches, permanent switches, split switches, independent cube control, and automatic rejoining. All algorithms operate on one shared immutable state model.

## 2. Problem formulation

### 2.1 State

A state contains:

```text
mode
positions
orientation
bridge_states
used_switches
active_cube
```

The state must include bridge and permanent-switch information because identical block coordinates can have different legal futures when the board configuration differs.

### 2.2 Initial state

The initial state is built from the selected level's start coordinate, initial bridge configuration, and empty used-switch set.

### 2.3 Actions

Normal states support:

```text
up, down, left, right
```

Split states additionally support:

```text
switch
```

The `switch` action changes which split cube is controlled.

### 2.4 Transition model

The transition model:

1. computes movement geometry;
2. rejects void and unsupported states;
3. applies fragile-tile rules;
4. activates relevant switches;
5. updates bridge and permanent-switch state;
6. processes split teleportation;
7. merges adjacent split cubes;
8. returns a new immutable state.

### 2.5 Goal test

A level is complete only when:

- the state is not split;
- orientation is upright;
- the occupied coordinate equals the goal.

### 2.6 Cost function

Final transition costs:

| Transition | Cost |
|---|---:|
| Normal roll | 1 |
| Split-cube movement | 1 |
| Switch active cube | 1 |
| Successor occupies a fragile tile | 3 |

The fragile penalty models risk and makes UCS optimize a different objective from BFS.

## 3. Algorithms

### 3.1 Breadth-First Search

BFS expands the shallowest frontier node first using a FIFO queue. With deterministic actions and repeated-state detection, BFS is complete on the finite state graph. It returns a solution with the minimum number of actions, but not necessarily the minimum weighted cost.

Complexity in graph-search terms:

```text
Time: O(V + E)
Space: O(V)
```

In the standard branching-factor notation, the worst case is exponential in solution depth.

### 3.2 Depth-First Search

DFS expands the most recently generated node using a stack. Its memory consumption is usually lower than BFS, but it is not optimal and can explore deep branches before finding a short solution.

### 3.3 Iterative Deepening Search

IDS repeats depth-limited DFS with increasing depth bounds. It finds the shallowest solution under unit depth while using memory closer to DFS.

### 3.4 Uniform-Cost Search

UCS uses a priority queue ordered by `g(n)`, the accumulated path cost. Because all transition costs are positive, UCS is complete and returns a least-cost solution.

The fragile-tile cost allows UCS to prefer a longer but safer route when available.

### 3.5 Greedy Best-First Search

Greedy Search orders the frontier by `h(n)` only. It may expand fewer nodes, but it is neither complete in every general graph setting nor optimal without additional restrictions.

### 3.6 A* Search

A* uses:

```text
f(n) = g(n) + h(n)
```

The final heuristic computes distances in a relaxed point-object graph:

- orientation constraints are removed;
- fragile restrictions are ignored;
- bridge cells are considered traversable;
- split-switch teleport edges are included.

If the relaxed distance is `d`, the base estimate is approximately:

```text
ceil(d / 2)
```

One normal roll can move an occupied cell by at most two grid edges. Removing constraints cannot make the relaxed problem harder than the real problem, so the estimate is a lower bound. The implementation also adds a safe orientation lower bound for non-upright states.

The test suite checks consistency on reachable split-level states and verifies that A* returns the same optimal cost as UCS on selected levels.

## 4. Advanced mechanics

### Fragile tiles

A lying normal block or a single split cube may occupy a fragile tile. An upright normal block breaks it and falls.

### Soft switches

Activated when any part of the block occupies the switch, including a single split cube.

### Heavy switches

Activated only by an upright normal block. A lying block or single split cube cannot activate one.

### Toggle bridges

Repeated activation alternates bridge state. Tests verify that two activations restore the original state.

### Permanent/one-time switches

Activated once by an upright normal block. Their identifiers are stored in `used_switches`, preventing later reactivation.

### Split switch

An upright normal block is teleported into two cubes. The player or solver moves one cube at a time and can change the active cube with `Space`. Adjacent cubes automatically rejoin.

## 5. Software design

Describe these modules and insert an architecture diagram:

- `game/state.py`
- `game/transition.py`
- `game/state_adapter.py`
- `game/board.py`
- `game/levels.py`
- `search_algorithms/problem.py`
- `search_algorithms/search_runner.py`
- `game/renderer.py`

Discuss why the renderer does not define search rules and why every solver uses the same `Problem`.

## 6. Testing

Run:

```bat
python -m unittest discover -s tests -p "test_*.py" -v
```

Final result:

```text
Tests run: [FINAL COUNT]
Result: OK
Runtime: [TIME]
```

Test categories:

- block movement
- state validation
- state conversion
- normal transitions
- advanced tiles
- bridge behavior
- split movement and rejoining
- advanced solver levels
- required fragile/permanent paths
- metrics and benchmark
- UCS cost and A* heuristic
- JSON level loading

## 7. Experimental setup

### Hardware and software

- CPU: `[CPU]`
- RAM: `[RAM]`
- Operating system: Windows `[version]`
- Python: `3.12.7`
- Pygame: `2.6.1`
- Repetitions per configuration: `5`

### Test groups

| Group | Level | Main mechanics |
|---|---|---|
| Basic | LEVEL1 | Standard movement |
| Fragile | LEVEL2 | Fragile surfaces |
| Soft bridge | LEVEL4 | Soft switch and bridge |
| Permanent | LEVEL6 | One-time/permanent switch |
| Heavy bridge | LEVEL9 | Heavy switches and bridges |
| Split | LEVEL10 | Split, independent cubes, rejoin |

### Metrics

- search time in milliseconds
- peak memory in megabytes
- expanded nodes
- solution length
- total path cost
- solved/error status

## 8. Results

Insert data from:

```text
benchmark_results/final/summary.csv
```

### 8.1 Summary table

| Level | Algorithm | Runs | Time mean | Memory mean | Expanded mean | Length mean | Cost mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `[level]` | `[algorithm]` | `[n]` | `[x]` | `[x]` | `[x]` | `[x]` | `[x]` |

### 8.2 Charts

Insert:

```text
benchmark_results/final/search_time_ms.png
benchmark_results/final/peak_memory_mb.png
benchmark_results/final/expanded_nodes.png
benchmark_results/final/solution_length.png
benchmark_results/final/total_cost.png
```

## 9. Discussion

Discuss observations such as:

- BFS and UCS can expand similar states on basic levels.
- Weighted fragile costs can cause UCS/A* to choose a path with different action length.
- DFS performance is highly sensitive to deterministic action order.
- A* should reduce expansions when the relaxed-distance heuristic is informative.
- Split levels enlarge the state because positions, active cube, bridges, and used switches all matter.
- Runtime measurements vary, while expanded-node counts remain deterministic for a fixed implementation and action order.

Do not claim that A* is always fastest unless the collected results support it.

## 10. Limitations and future work

Possible limitations:

- 2.5D rather than hardware-accelerated 3D rendering
- heuristic relaxation can be weak on complex bridge configurations
- fixed handcrafted level collection
- no online level editor
- benchmark time includes Python measurement overhead
- DFS may require timeouts on difficult levels

Possible future improvements:

- stronger pattern-database heuristic
- level editor
- additional validated combined-mechanic levels
- animation interpolation
- configurable cost models
- automated CI benchmark artifacts

## 11. Conclusion

Summarize:

- complete shared state-space formulation
- support for advanced mechanics
- successful integration of classical search algorithms
- correctness evidence from tests
- comparative benchmark findings
- main architectural and UI contributions

## 12. Contribution table

Copy the final data from `docs/CONTRIBUTIONS.md`.

## 13. AI usage disclosure

Summarize `docs/AI_USAGE.md`.

## References

1. Pedro Jorge, *EIACD Roll the Block*, GitHub repository.
2. Ege Alpay, *Bloxorz Solver*, GitLab repository.
3. Erroler, *Bloxorz*, GitHub repository.
4. Stuart Russell and Peter Norvig, *Artificial Intelligence: A Modern Approach*.
5. Pygame documentation.
6. Python documentation.

Use the citation style requested by the instructor.
