from __future__ import annotations

from ..grid_utils import neighbors
from ..models import MazeProblem, Pos, SearchResult
from ..path_utils import reconstruct_path


def dfs(problem: MazeProblem) -> SearchResult:
    stack: list[Pos] = [problem.start]
    parent: dict[Pos, Pos | None] = {problem.start: None}
    visited: set[Pos] = set()
    visited_count = 0

    while stack:
        node = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        visited_count += 1

        if node == problem.end:
            path = reconstruct_path(parent, node)
            return SearchResult("DFS", True, path, visited_count, "success", len(path) - 1)

        for nxt in reversed(neighbors(problem, node)):
            if nxt not in visited and nxt not in parent:
                parent[nxt] = node
                stack.append(nxt)

    return SearchResult("DFS", False, [], visited_count, "failure", -1)
