from __future__ import annotations

from .constants import GOAL_STATE, N, SIZE
from .types import Move, State


def validate_state(state: State) -> None:
    if len(state) != SIZE:
        raise ValueError(f"state length must be {SIZE}, got {len(state)}")
    if set(state) != set(range(SIZE)):
        raise ValueError("state must contain each number 0..15 exactly once")


def is_goal(state: State) -> bool:
    return state == GOAL_STATE


def inversion_count(state: State) -> int:
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        ai = arr[i]
        for j in range(i + 1, len(arr)):
            if ai > arr[j]:
                inv += 1
    return inv


def is_solvable(state: State) -> bool:
    validate_state(state)
    inv = inversion_count(state)
    blank_idx = state.index(0)
    blank_row_from_top = blank_idx // N
    blank_row_from_bottom = N - blank_row_from_top
    if blank_row_from_bottom % 2 == 1:
        return inv % 2 == 0
    return inv % 2 == 1


def get_neighbors(state: State) -> list[tuple[Move, State]]:
    blank = state.index(0)
    r, c = divmod(blank, N)
    neighbors: list[tuple[Move, State]] = []

    def swapped(new_blank: int) -> State:
        arr = list(state)
        arr[blank], arr[new_blank] = arr[new_blank], arr[blank]
        return tuple(arr)

    if r > 0:
        neighbors.append(("U", swapped(blank - N)))
    if r < N - 1:
        neighbors.append(("D", swapped(blank + N)))
    if c > 0:
        neighbors.append(("L", swapped(blank - 1)))
    if c < N - 1:
        neighbors.append(("R", swapped(blank + 1)))
    return neighbors


def apply_moves(state: State, moves: list[Move]) -> State:
    cur = state
    for mv in moves:
        next_state = None
        for move, nxt in get_neighbors(cur):
            if move == mv:
                next_state = nxt
                break
        if next_state is None:
            raise ValueError(f"invalid move {mv} for state {cur}")
        cur = next_state
    return cur

