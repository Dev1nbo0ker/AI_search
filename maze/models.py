from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Pos = tuple[int, int]


@dataclass
class MazeProblem:
    """Maze definition: grid + start/end + shape."""

    grid: list[list[str]]
    start: Pos
    end: Pos
    rows: int
    cols: int


@dataclass
class SearchResult:
    """Shared search result format across all algorithms."""

    algorithm: str
    found: bool
    path: list[Pos]
    visited_count: int
    status: Literal["success", "failure", "cutoff"]
    depth: int
