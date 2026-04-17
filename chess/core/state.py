from __future__ import annotations

from dataclasses import dataclass

from .board import Board
from .enums import GameResult


@dataclass
class GameState:
    board: Board
    result: GameResult = GameResult.ONGOING
    move_count: int = 0

