from __future__ import annotations

from .board import apply_moves
from .constants import GOAL_STATE
from .types import State


def default_cases() -> list[tuple[str, State]]:
    case_goal = GOAL_STATE
    case_one_move = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    scramble = ["L", "U", "L", "U", "R", "D", "L", "D", "R", "U", "R", "D"]
    case_medium = apply_moves(GOAL_STATE, scramble)

    return [
        ("Already Goal", case_goal),
        ("One Move Away", case_one_move),
        ("Medium Solvable", case_medium),
    ]

