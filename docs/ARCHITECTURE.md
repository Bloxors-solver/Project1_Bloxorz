# Architecture

## Overview

The project separates game rules, state transitions, search algorithms, rendering, metrics, and data files.

```text
JSON level data
      ↓
Levels / Board
      ↓
GameState ←→ state_adapter ←→ legacy Block view
      ↓
transition(state, action, level)
      ↓
Problem API
      ↓
BFS / DFS / IDS / UCS / Greedy / A*
      ↓
SearchResult / benchmark / GUI replay
```

## GameState

`GameState` is immutable and hashable, so it can be stored safely in `set` and `dict` structures.

Main fields:

- `mode`: normal or split
- `positions`: occupied board coordinates
- `orientation`: upright, horizontal, vertical, or split
- `bridge_states`: deterministic bridge configuration
- `used_switches`: permanent/one-time switches already used
- `active_cube`: controlled cube in split mode

The complete dynamic configuration belongs to the state. Therefore, two geometrically identical block positions with different bridge or switch configurations remain distinct search states.

## Transition model

`transition(state, action, level_name)` is the source of truth for legal state changes.

Typical order:

1. Apply movement geometry.
2. Reject void/out-of-bounds states.
3. Reject upright normal block on fragile tile.
4. Detect soft/heavy/permanent/split switch activation.
5. Update bridge and used-switch information.
6. Move split cube or change the active cube.
7. Rejoin adjacent split cubes.
8. Return a new immutable state.

Invalid transitions return `None`.

## Problem API

The shared `Problem` class provides:

- `initial`
- `actions(state)`
- `result(state, action)`
- `action_cost(state, action, next_state)`
- `is_goal(state)`
- expanded-node metrics

Every solver receives the same API and the same parsed level data.

## Search algorithms

### BFS

Uses a FIFO frontier and repeated-state set. It is complete for the finite reachable state graph and finds the minimum number of actions when depth is the objective.

### DFS

Uses a LIFO frontier. It may find a solution quickly but is not optimal and can expand deep unproductive paths.

### IDS

Repeats depth-limited DFS with increasing limits. It retains DFS-like memory use while finding the shallowest solution under unit depth.

### UCS

Orders nodes by accumulated path cost `g(n)`.

Final cost model:

- normal action: `1`
- successor touches fragile tile: `3`

UCS returns a least-cost solution for positive action costs.

### Greedy Search

Orders nodes using only `h(n)`. It is fast on some levels but is not guaranteed to return an optimal solution.

### A*

Uses:

```text
f(n) = g(n) + h(n)
```

The heuristic is derived from a relaxed point graph. It ignores constraints that can only make the real problem harder and includes split-switch teleport edges. The implementation stores the cheapest known `g` value per state and skips stale priority-queue entries.

## Metrics

`run_search` records:

- solved status
- action sequence
- solution length
- total path cost
- search time in milliseconds
- peak memory in megabytes
- expanded nodes

Metrics are separated from rendering so benchmark runs and GUI runs use the same measurement pipeline.

## Rendering

The renderer presents an isometric 2.5D view. It does not define game rules. It reads `GameState`, draws the board, and sends user actions to the transition layer.

The AI replay uses the action sequence returned by a solver. Pause/Resume affects playback only and does not alter the solution.

## Testing strategy

Tests are grouped into:

- movement geometry
- level safety
- state validation
- state adapters
- normal transitions
- advanced tiles
- split logic
- split transitions
- solver integration
- advanced solver levels
- required-tile solver paths
- metrics and benchmark export
- UCS cost and A* heuristic
- JSON level loading
