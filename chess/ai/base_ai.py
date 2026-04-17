from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from AI_search.chess.core.board import Board
from AI_search.chess.core.enums import Side
from AI_search.chess.core.move import Move


class BaseAI(ABC):
    @abstractmethod
    def choose_move(self, board: Board, side: Side) -> Optional[Move]:
        raise NotImplementedError

