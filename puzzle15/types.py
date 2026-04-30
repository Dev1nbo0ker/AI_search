from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

State = tuple[int, ...]
Move = str
HeuristicFunc = Callable[[State], int]


@dataclass
class SearchResult:
    algorithm: str
    heuristic_name: str
    solvable: bool
    solution_length: int
    moves: list[Move]
    expanded_nodes: int
    running_time: float

