from __future__ import annotations

from enum import Enum


class Side(Enum):
    RED = 1
    BLACK = -1

    @property
    def opponent(self) -> "Side":
        return Side.BLACK if self is Side.RED else Side.RED

    @property
    def forward(self) -> int:
        # Red starts at bottom and moves upward (row decreases).
        return -1 if self is Side.RED else 1

    @property
    def label(self) -> str:
        return "红方" if self is Side.RED else "黑方"


class PieceType(Enum):
    GENERAL = "general"   # 将/帅
    ADVISOR = "advisor"   # 士/仕
    ELEPHANT = "elephant" # 象/相
    HORSE = "horse"       # 马
    ROOK = "rook"         # 车
    CANNON = "cannon"     # 炮
    PAWN = "pawn"         # 兵/卒


class ControlType(Enum):
    HUMAN = "human"
    RULE_AI = "rule_ai"
    ALPHABETA_AI = "alphabeta_ai"


class GameResult(Enum):
    ONGOING = "ongoing"
    RED_WIN = "red_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"

