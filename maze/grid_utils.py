from __future__ import annotations

from .models import MazeProblem, Pos


def in_bounds(problem: MazeProblem, pos: Pos) -> bool:
    r, c = pos
    return 0 <= r < problem.rows and 0 <= c < problem.cols


def is_passable(problem: MazeProblem, pos: Pos) -> bool:
    r, c = pos
    return problem.grid[r][c] != "1"


def neighbors(problem: MazeProblem, pos: Pos) -> list[Pos]:
    """Neighbor order is fixed for reproducibility: up, right, down, left."""
    r, c = pos
    order = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    result: list[Pos] = []
    for dr, dc in order:
        nxt = (r + dr, c + dc)
        if in_bounds(problem, nxt) and is_passable(problem, nxt):
            result.append(nxt)
    return result
