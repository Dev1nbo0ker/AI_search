from __future__ import annotations

from .types import Move, State

N = 4
SIZE = N * N
GOAL_STATE: State = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

GOAL_POS: dict[int, tuple[int, int]] = {
    tile: divmod(idx, N) for idx, tile in enumerate(GOAL_STATE) if tile != 0
}

REVERSE_MOVE: dict[Move, Move] = {"U": "D", "D": "U", "L": "R", "R": "L"}

# 5-5-5 disjoint patterns for additive PDB.
PDB_PATTERNS: tuple[tuple[int, ...], ...] = (
    (1, 2, 3, 4, 5),
    (6, 7, 8, 9, 10),
    (11, 12, 13, 14, 15),
)

BLANK_ADJ: tuple[tuple[int, ...], ...] = tuple(
    tuple(
        nxt
        for nxt in (
            idx - N if idx // N > 0 else -1,
            idx + N if idx // N < N - 1 else -1,
            idx - 1 if idx % N > 0 else -1,
            idx + 1 if idx % N < N - 1 else -1,
        )
        if nxt != -1
    )
    for idx in range(SIZE)
)

