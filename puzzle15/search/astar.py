from __future__ import annotations

from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from ..board import get_neighbors, is_goal, is_solvable, validate_state
from ..types import HeuristicFunc, Move, SearchResult, State


def _reconstruct_path(
    parent: dict[State, tuple[State, Move] | None], end_state: State
) -> list[Move]:
    moves: list[Move] = []
    cur = end_state
    while True:
        entry = parent[cur]
        if entry is None:
            break
        prev, move = entry
        moves.append(move)
        cur = prev
    moves.reverse()
    return moves


def astar(start: State, heuristic: HeuristicFunc) -> SearchResult:
    validate_state(start)
    t0 = perf_counter()
    h_name = getattr(heuristic, "__name__", "heuristic")

    if not is_solvable(start):
        return SearchResult("A*", h_name, False, 0, [], 0, perf_counter() - t0)

    open_heap: list[tuple[int, int, int, State]] = []
    g_score: dict[State, int] = {start: 0}
    parent: dict[State, tuple[State, Move] | None] = {start: None}
    expanded_nodes = 0
    tie = count()

    heappush(open_heap, (heuristic(start), 0, next(tie), start))

    while open_heap:
        _, g_cur, _, state = heappop(open_heap)
        best_g = g_score.get(state)
        if best_g is None or g_cur != best_g:
            continue

        if is_goal(state):
            path = _reconstruct_path(parent, state)
            return SearchResult(
                "A*",
                h_name,
                True,
                len(path),
                path,
                expanded_nodes,
                perf_counter() - t0,
            )

        expanded_nodes += 1
        for move, nxt in get_neighbors(state):
            ng = g_cur + 1
            old = g_score.get(nxt)
            if old is None or ng < old:
                g_score[nxt] = ng
                parent[nxt] = (state, move)
                heappush(open_heap, (ng + heuristic(nxt), ng, next(tie), nxt))

    return SearchResult("A*", h_name, False, 0, [], expanded_nodes, perf_counter() - t0)

