# Level JSON format

Each playable level is stored as `levels/levelN.json`.

## Required fields

```json
{
  "schema_version": 1,
  "name": "LEVEL1",
  "layout": [[-1, -1], [-1, 0]],
  "start": [1, 1],
  "goal": [1, 1],
  "buttons": [],
  "split_switches": []
}
```

## Tile codes

| Code | Meaning |
|---:|---|
| `-2` | Closed bridge / hidden path |
| `-1` | Void |
| `0` | Floor |
| `3` | Fragile tile |
| `4` | Heavy switch |
| `5` | Soft switch |
| `6` | Permanent/one-time heavy switch |
| `7` | Goal |
| `8` | Split switch |

## Button definition

```json
{
  "position": [3, 10],
  "initial_state": true,
  "bridges": [[3, 7], [3, 8]]
}
```

- `position`: switch coordinate
- `initial_state`: initial open/closed bridge state used by the existing game model
- `bridges`: bridge cells controlled by the switch

## Split switch

```json
{
  "position": [3, 5],
  "destinations": [[2, 7], [4, 9]]
}
```

An upright normal block on the split switch becomes two cubes at the listed destinations.

## Validation

The loader should reject:

- non-rectangular layouts
- missing start or goal
- unsupported tile values
- out-of-range coordinates
- malformed buttons
- split switches without exactly two destinations

The same parsed level object must be used by manual play and all search algorithms.
