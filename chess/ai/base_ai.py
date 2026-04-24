from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from chess.core.board import Board
from chess.core.enums import Side
from chess.core.move import Move


class BaseAI(ABC):
    @abstractmethod
    def choose_move(self, board: Board, side: Side) -> Optional[Move]:
        raise NotImplementedError

