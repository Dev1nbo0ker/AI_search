from __future__ import annotations

from ..constants import GOAL_POS, N
from ..types import State


def manhattan_distance(state: State) -> int:
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(idx, N)
        gr, gc = GOAL_POS[tile]
        dist += abs(r - gr) + abs(c - gc)
    return dist


def linear_conflict(state: State) -> int:
    conflict = 0

    for row in range(N):
        row_tiles: list[int] = []
        for col in range(N):
            tile = state[row * N + col]
            if tile == 0:
                continue
            goal_row, _ = GOAL_POS[tile]
            if goal_row == row:
                row_tiles.append(tile)
        for i in range(len(row_tiles)):
            _, goal_col_i = GOAL_POS[row_tiles[i]]
            for j in range(i + 1, len(row_tiles)):
                _, goal_col_j = GOAL_POS[row_tiles[j]]
                if goal_col_i > goal_col_j:
                    conflict += 2

    for col in range(N):
        col_tiles: list[int] = []
        for row in range(N):
            tile = state[row * N + col]
            if tile == 0:
                continue
            _, goal_col = GOAL_POS[tile]
            if goal_col == col:
                col_tiles.append(tile)
        for i in range(len(col_tiles)):
            goal_row_i, _ = GOAL_POS[col_tiles[i]]
            for j in range(i + 1, len(col_tiles)):
                goal_row_j, _ = GOAL_POS[col_tiles[j]]
                if goal_row_i > goal_row_j:
                    conflict += 2

    return conflict


def heuristic_manhattan(state: State) -> int:
    return manhattan_distance(state)


def heuristic_manhattan_linear_conflict(state: State) -> int:
    return manhattan_distance(state) + linear_conflict(state)

