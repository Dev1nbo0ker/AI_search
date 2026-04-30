from __future__ import annotations

from collections import deque

from ..grid_utils import neighbors
from ..models import MazeProblem, Pos, SearchResult
from ..path_utils import merge_bidirectional_path


def _expand_one_step(
    problem: MazeProblem,
    frontier: deque[Pos],
    visited_this: set[Pos],
    visited_other: set[Pos],
    parent_this: dict[Pos, Pos | None],
) -> tuple[Pos | None, int]:
    if not frontier:
        return None, 0

    node = frontier.popleft()
    expanded_count = 1

    for nxt in neighbors(problem, node):
        if nxt in visited_this:
            continue
        visited_this.add(nxt)
        parent_this[nxt] = node
        if nxt in visited_other:
            return nxt, expanded_count
        frontier.append(nxt)

    return None, expanded_count


def bidirectional_search(problem: MazeProblem) -> SearchResult:
    if problem.start == problem.end:
        return SearchResult("Bidirectional", True, [problem.start], 1, "success", 0)

    frontier_fwd: deque[Pos] = deque([problem.start])
    frontier_bwd: deque[Pos] = deque([problem.end])
    visited_fwd: set[Pos] = {problem.start}
    visited_bwd: set[Pos] = {problem.end}
    parent_fwd: dict[Pos, Pos | None] = {problem.start: None}
    parent_bwd: dict[Pos, Pos | None] = {problem.end: None}
    visited_count = 0

    while frontier_fwd and frontier_bwd:
        if len(frontier_fwd) <= len(frontier_bwd):
            meet, expanded = _expand_one_step(
                problem, frontier_fwd, visited_fwd, visited_bwd, parent_fwd
            )
        else:
            meet, expanded = _expand_one_step(
                problem, frontier_bwd, visited_bwd, visited_fwd, parent_bwd
            )

        visited_count += expanded
        if meet is not None:
            path = merge_bidirectional_path(parent_fwd, parent_bwd, meet)
            return SearchResult(
                "Bidirectional", True, path, visited_count, "success", len(path) - 1
            )

    return SearchResult("Bidirectional", False, [], visited_count, "failure", -1)
