from __future__ import annotations

from time import perf_counter

from ..board import get_neighbors, is_goal, is_solvable, validate_state
from ..constants import REVERSE_MOVE
from ..types import HeuristicFunc, Move, SearchResult, State


def idastar(start: State, heuristic: HeuristicFunc) -> SearchResult:
    validate_state(start)
    t0 = perf_counter()
    h_name = getattr(heuristic, "__name__", "heuristic")

    if not is_solvable(start):
        return SearchResult("IDA*", h_name, False, 0, [], 0, perf_counter() - t0)

    found = object()
    expanded_nodes = 0
    bound = heuristic(start)
    path_moves: list[Move] = []
    path_states: set[State] = {start}

    def dfs(state: State, g: int, threshold: int, prev_move: Move | None) -> object:
        nonlocal expanded_nodes
        f = g + heuristic(state)
        if f > threshold:
            return f
        if is_goal(state):
            return found

        expanded_nodes += 1
        min_exceed = float("inf")

        for move, nxt in get_neighbors(state):
            if prev_move is not None and move == REVERSE_MOVE[prev_move]:
                continue
            if nxt in path_states:
                continue

            path_states.add(nxt)
            path_moves.append(move)
            res = dfs(nxt, g + 1, threshold, move)

            if res is found:
                return found
            if isinstance(res, (int, float)) and res < min_exceed:
                min_exceed = res

            path_moves.pop()
            path_states.remove(nxt)

        return min_exceed

    while True:
        res = dfs(start, 0, bound, None)
        if res is found:
            return SearchResult(
                "IDA*",
                h_name,
                True,
                len(path_moves),
                path_moves.copy(),
                expanded_nodes,
                perf_counter() - t0,
            )
        if not isinstance(res, (int, float)) or res == float("inf"):
            return SearchResult(
                "IDA*",
                h_name,
                False,
                0,
                [],
                expanded_nodes,
                perf_counter() - t0,
            )
        bound = int(res)

