from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chess.ai.alphabeta_ai import AlphaBetaAI
from chess.ai.base_ai import BaseAI
from chess.ai.rule_ai import RuleAI
from chess.core.board import Board
from chess.core.enums import ControlType, Side
from chess.core.move import Move


@dataclass
class Player:
    side: Side
    control_type: ControlType
    ai: Optional[BaseAI] = None

    @property
    def is_human(self) -> bool:
        return self.control_type is ControlType.HUMAN

    def choose_move(self, board: Board) -> Optional[Move]:
        if self.is_human or self.ai is None:
            return None
        return self.ai.choose_move(board, self.side)

    @property
    def label(self) -> str:
        return f"{self.side.label}({self.control_type.value})"


def create_player(side: Side, control_type: ControlType, depth: int = 3) -> Player:
    if control_type is ControlType.HUMAN:
        return Player(side=side, control_type=control_type, ai=None)
    if control_type is ControlType.RULE_AI:
        return Player(side=side, control_type=control_type, ai=RuleAI())
    return Player(side=side, control_type=control_type, ai=AlphaBetaAI(depth=depth))

