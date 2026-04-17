from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .piece import Piece


@dataclass
class Move:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    moved_piece: Optional[Piece] = None
    captured_piece: Optional[Piece] = None
    is_check: bool = False
    score_hint: int = 0

    @property
    def key(self) -> tuple[int, int, int, int]:
        return (self.from_row, self.from_col, self.to_row, self.to_col)

