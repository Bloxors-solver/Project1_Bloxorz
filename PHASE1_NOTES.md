# Phase 1 — Baseline stabilization

This phase intentionally avoids changing the visual design or search-state model.
Its purpose is to make the existing movement and board foundation deterministic and safe before adding split blocks and richer bridge state.

## Changes

- Fixed board boundary checks (`<` instead of `<=`).
- Prevented block rendering from indexing outside the level matrix after a losing move.
- Refreshed all metadata when switching levels.
- Fixed row/column bounds in the goal-island flood fill.
- Changed successor generation from `set` to ordered `list`.
- Added input validation for movement directions.
- Added automated tests for all 12 orientation/direction transitions.
- Added safety tests for matrix boundaries, falling moves, level switching, and expansion order.

## Run tests

From the project root with the virtual environment activated:

```bat
python -m unittest discover -s tests -v
```

## Manual smoke test

```bat
python main.py
```

Check at least:

1. Start and restart a level.
2. Move off an edge and confirm the game shows Game Over without crashing.
3. Complete a level and advance to the next level.
4. Run BFS and DFS twice on the same level and confirm their behavior is repeatable.
