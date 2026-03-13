# AoE2 DE AI Scripting - Objects Reference (from airef.github.io)

## Dock Units (Naval)

| ID | Name | AI Name | Line | Class | Age |
|---|---|---|---|---|---|
| 13 | Fishing Ship | fishing-ship | - | fishing-ship-class | 1 |
| 17 | Trade Cog | trade-cog | - | trade-cog-class | 2 |
| 545 | Transport Ship | transport-ship | - | transport-ship-class | 2 |
| 539 | Galley | galley | galley-line | warship-class | 2 |
| 21 | War Galley | war-galley | galley-line | warship-class | 3 |
| 442 | Galleon | galleon | galley-line | warship-class | 4 |
| 1103 | Fire Galley | fire-galley | fire-ship-line | warship-class | 2 |
| 529 | Fire Ship | fire-ship | fire-ship-line | warship-class | 3 |
| 532 | Fast Fire Ship | fast-fire-ship | fire-ship-line | warship-class | 4 |
| 1104 | Demolition Raft | demo-raft | demolition-ship-line | warship-class | 2 |
| 527 | Demolition Ship | demolition-ship | demolition-ship-line | warship-class | 3 |
| 528 | Heavy Demolition Ship | heavy-demolition-ship | demolition-ship-line | warship-class | 4 |
| 420 | Cannon Galleon | cannon-galleon | cannon-galleon-line | warship-class | 4 |
| 691 | Elite Cannon Galleon | elite-cannon-galleon | cannon-galleon-line | warship-class | 4 |
| 831 | Turtle Ship | turtle-ship | turtle-ship-line | warship-class | 3 |
| 832 | Elite Turtle Ship | elite-turtle-ship | turtle-ship-line | warship-class | 4 |
| 1004 | Caravel | caravel | caravel-line | warship-class | 3 |
| 1006 | Elite Caravel | elite-caravel | caravel-line | warship-class | 4 |
| 250 | Longboat | longboat | longboat-line | warship-class | 3 |
| 533 | Elite Longboat | elite-longboat | longboat-line | warship-class | 4 |
| 1795 | Dromon | dromon | - | warship-class | 4 |
| 1750 | Thirisadai | thirisadai | - | warship-class | 4 |

## Key Line Names for Training

- `galley-line` → trains best of: Galley / War Galley / Galleon
- `fire-ship-line` → trains best of: Fire Galley / Fire Ship / Fast Fire Ship
- `demolition-ship-line` → trains best of: Demo Raft / Demolition Ship / Heavy Demo Ship
- `cannon-galleon-line` → trains best of: Cannon Galleon / Elite Cannon Galleon

## Important Notes

- Demolition Raft AI name is `demo-raft` (NOT `demolition-raft`)
- In WK, Fire Galley uses same ID as AoC Fire Ship (529), defined as "fire-ship"
- In WK, Demolition Raft uses same ID as AoC Demolition Ship (527), defined as "demolition-ship"
- Elite Cannon Galleon requires Chemistry research
