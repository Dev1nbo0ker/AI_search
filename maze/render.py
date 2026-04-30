from __future__ import annotations

from .models import MazeProblem, SearchResult


def render_path(problem: MazeProblem, path: list[tuple[int, int]]) -> str:
    display = [row[:] for row in problem.grid]
    for r, c in path:
        if display[r][c] not in {"S", "E"}:
            display[r][c] = "*"
    return "\n".join("".join(row) for row in display)


def print_result(problem: MazeProblem, result: SearchResult) -> None:
    print(f"[{result.algorithm}]")
    print(f"status: {result.status}")
    print(f"visited nodes: {result.visited_count}")
    if result.found:
        print(f"path length: {result.depth}")
        print(f"path: {result.path}")
        print(render_path(problem, result.path))
    else:
        print("No path found.")
        print(render_path(problem, []))
    print("-" * 40)
