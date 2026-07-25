# Requirements audit

Update the final test count and manual-check status before submission.

| Requirement | Implementation | Evidence |
|---|---|---|
| Upright/horizontal/vertical movement | `game/block.py`, `game/transition.py` | `tests/test_block_movement.py`, `tests/test_transition.py` |
| Void and goal rules | transition and goal test | `tests/test_transition.py` |
| Fragile tiles | advanced-tile transition rules | `tests/test_advanced_tiles.py`, `tests/test_solver_required_tiles.py` |
| Bridges | bridge state inside `GameState` | `tests/test_state.py`, `tests/test_state_adapter.py` |
| Soft switches | normal and split activation | `tests/test_advanced_tiles.py`, `tests/test_split_transition.py` |
| Heavy switches | upright normal block only | `tests/test_advanced_tiles.py`, `tests/test_split_transition.py` |
| Toggle behavior | bridge state flips repeatedly | `tests/test_advanced_tiles.py` |
| Permanent/one-time behavior | records use and preserves final state | `tests/test_advanced_tiles.py`, `tests/test_solver_required_tiles.py` |
| Split switch | upright activation and teleport | `tests/test_split_switch.py` |
| Active-cube switching | `Space` action | `tests/test_split_logic.py`, `tests/test_split_transition.py` |
| Automatic rejoining | adjacent cubes merge | `tests/test_split_logic.py`, `tests/test_split_transition.py` |
| Single cube restrictions | no heavy switch or goal | split transition tests |
| BFS | search module | integration and advanced solver tests |
| DFS/IDS | search modules | integration/manual benchmark |
| UCS | non-uniform action cost | `tests/test_cost_and_heuristic.py` |
| A* | relaxed admissible heuristic | `tests/test_cost_and_heuristic.py` |
| Repeated-state handling | immutable full state | state and integration tests |
| Metrics | `SearchResult` and `run_search` | `tests/test_search_metrics.py` |
| Benchmark CSV | `benchmark.py` | `tests/test_benchmark.py` |
| Run All comparison | comparison module and GUI | `tests/test_comparison.py` + manual check |
| JSON level format | loader and JSON files | `tests/test_level_json_loader.py` |
| New Game and Restart | renderer/input handler | manual GUI check |
| AI Pause/Resume | renderer/input handler | manual GUI check |

## Final automated result

```text
Date: [YYYY-MM-DD]
Python: [version]
Tests: [count]
Result: OK
```

Command:

```bat
python -m unittest discover -s tests -p "test_*.py" -v
```

## Final manual checklist

- [ ] Human Level 1
- [ ] Fragile level
- [ ] Soft-switch bridge level
- [ ] Heavy-switch bridge level
- [ ] Permanent/one-time switch level
- [ ] Split Level 10 and Space control
- [ ] BFS replay
- [ ] UCS replay
- [ ] A* split replay
- [ ] Pause and Resume AI
- [ ] Restart
- [ ] New Game
- [ ] Run All and CSV export
