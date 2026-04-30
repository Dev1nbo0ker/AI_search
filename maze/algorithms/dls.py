from __future__ import annotations

from ..grid_utils import neighbors
from ..models import MazeProblem, Pos, SearchResult


def depth_limited_search(problem: MazeProblem, limit: int) -> SearchResult:
    if limit < 0:
        raise ValueError("Depth limit must be >= 0.")

    expanded_nodes: set[Pos] = set()

    def recurse(node: Pos, depth: int, path: list[Pos], path_set: set[Pos]) -> tuple[str, list[Pos]]:
        expanded_nodes.add(node)
        if node == problem.end:
            return "success", path.copy()
        if depth == limit:
            return "cutoff", []

        cutoff_occurred = False
        for nxt in neighbors(problem, node):
            if nxt in path_set:
                continue
            path.append(nxt)
            path_set.add(nxt)
            status, result_path = recurse(nxt, depth + 1, path, path_set)
            if status == "success":
                return status, result_path
            if status == "cutoff":
                cutoff_occurred = True
            path.pop()
            path_set.remove(nxt)

        if cutoff_occurred:
            return "cutoff", []
        return "failure", []

    status, path = recurse(problem.start, 0, [problem.start], {problem.start})
    found = status == "success"
    depth = len(path) - 1 if found else -1
    return SearchResult("DLS", found, path if found else [], len(expanded_nodes), status, depth)
