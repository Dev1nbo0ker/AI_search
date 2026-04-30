from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from cn_chess.core.board import Board
from cn_chess.core.enums import Side
from cn_chess.core.move import Move


class BaseAI(ABC):
    @abstractmethod
    def choose_move(self, board: Board, side: Side) -> Optional[Move]:
        raise NotImplementedError

