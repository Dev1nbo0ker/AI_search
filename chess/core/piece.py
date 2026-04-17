from __future__ import annotations

from dataclasses import dataclass

from .enums import PieceType, Side


@dataclass(frozen=True)
class Piece:
    piece_type: PieceType
    side: Side

