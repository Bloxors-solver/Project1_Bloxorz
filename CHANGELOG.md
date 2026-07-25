# Changelog

## Phase 7 — Compliance and finalization

- Added advanced-tile compliance tests
- Fixed one-time heavy switch activation while the normal block is lying
- Added solver tests for bridge, fragile, permanent, and split mechanics
- Added non-uniform UCS/A* transition costs
- Added a relaxed-graph A* heuristic and consistency/optimality tests
- Added JSON level loading and validation
- Finalized isometric block proportions and menu alignment
- Added final README, attribution, report draft, benchmark summary, release packaging, and GitHub publishing documentation

## Phase 6 — Metrics and comparison

- Unified search metrics
- Added GUI search-statistics panel
- Prevented stale metrics across levels
- Added Run All comparison for BFS, DFS, UCS, and A*
- Added CSV export and A* replay

## Phase 5 — Advanced split mechanics

- Added split-state representation
- Added active-cube switching
- Added split-cube movement and automatic rejoining
- Added Level 10 split switch
- Integrated split play with GUI and solvers
- Added split-specific tests

## Phase 4 — Benchmarking

- Added repeatable benchmark runs
- Added CSV export
- Added time, memory, expanded-node, solution-length, and total-cost metrics

## Phases 1–3 — Core redesign

- Established stable project environment
- Added immutable `GameState`
- Unified manual and search transitions
- Refactored BFS, DFS, UCS, and A* to use shared state
- Added state, movement, transition, and integration tests
