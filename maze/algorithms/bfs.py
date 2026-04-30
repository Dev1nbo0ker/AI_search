from __future__ import annotations

from collections import deque

from ..grid_utils import neighbors
from ..models import MazeProblem, Pos, SearchResult
from ..path_utils import reconstruct_path


def bfs(problem: MazeProblem) -> SearchResult:
    queue: deque[Pos] = deque([problem.start])
    visited: set[Pos] = {problem.start}
    parent: dict[Pos, Pos | None] = {problem.start: None}
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1

        if node == problem.end:
            path = reconstruct_path(parent, node)
            return SearchResult("BFS", True, path, visited_count, "success", len(path) - 1)

        for nxt in neighbors(problem, node):
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = node
                queue.append(nxt)

    return SearchResult("BFS", False, [], visited_count, "failure", -1)
