from __future__ import annotations

from typing import Literal

from ..models import MazeProblem, SearchResult
from .dls import depth_limited_search


def iterative_deepening_search(problem: MazeProblem, max_depth: int | None = None) -> SearchResult:
    if max_depth is None:
        max_depth = problem.rows * problem.cols
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0.")

    total_visited = 0
    last_status: Literal["success", "failure", "cutoff"] = "failure"

    for limit in range(max_depth + 1):
        result = depth_limited_search(problem, limit)
        total_visited += result.visited_count
        last_status = result.status

        if result.found:
            return SearchResult("IDS", True, result.path, total_visited, "success", result.depth)
        if result.status == "failure":
            return SearchResult("IDS", False, [], total_visited, "failure", -1)

    return SearchResult("IDS", False, [], total_visited, last_status, -1)
