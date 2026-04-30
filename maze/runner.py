from __future__ import annotations

from .algorithms import (
    bfs,
    bidirectional_search,
    depth_limited_search,
    dfs,
    iterative_deepening_search,
)
from .models import MazeProblem, SearchResult
from .render import print_result


def run_all(problem: MazeProblem, dls_limit: int, ids_max_depth: int | None = None) -> list[SearchResult]:
    results = [
        dfs(problem),
        bfs(problem),
        depth_limited_search(problem, dls_limit),
        iterative_deepening_search(problem, ids_max_depth),
        bidirectional_search(problem),
    ]

    print(f"DLS limit = {dls_limit}")
    if ids_max_depth is not None:
        print(f"IDS max_depth = {ids_max_depth}")
    print("=" * 40)
    for result in results:
        print_result(problem, result)

    return results
