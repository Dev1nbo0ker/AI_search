from __future__ import annotations

# Backward-compatible facade for the refactored package.
# You can still run this file directly: python puzzle.py

from puzzle15.board import (
    apply_moves,
    get_neighbors,
    inversion_count,
    is_goal,
    is_solvable,
    validate_state,
)
from puzzle15.cases import default_cases
from puzzle15.constants import GOAL_STATE
from puzzle15.experiment import format_benchmark_table, format_result, run_benchmark_experiment
from puzzle15.heuristics import (
    ensure_pdb_built,
    heuristic_manhattan,
    heuristic_manhattan_linear_conflict,
    heuristic_pdb,
    linear_conflict,
    manhattan_distance,
)
from puzzle15.search import astar, idastar
from puzzle15.types import HeuristicFunc, Move, SearchResult, State

__all__ = [
    "State",
    "Move",
    "HeuristicFunc",
    "SearchResult",
    "GOAL_STATE",
    "validate_state",
    "is_goal",
    "inversion_count",
    "is_solvable",
    "get_neighbors",
    "apply_moves",
    "manhattan_distance",
    "linear_conflict",
    "heuristic_manhattan",
    "heuristic_manhattan_linear_conflict",
    "heuristic_pdb",
    "ensure_pdb_built",
    "astar",
    "idastar",
    "format_result",
    "format_benchmark_table",
    "run_benchmark_experiment",
    "default_cases",
]


def main() -> None:
    run_benchmark_experiment(default_cases())


if __name__ == "__main__":
    main()

