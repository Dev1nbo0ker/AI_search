from __future__ import annotations

from cn_chess.core.enums import PieceType, Side
from cn_chess.core.move import Move

from .evaluator import piece_value


def _move_order_score(move: Move, side: Side) -> int:
    score = 0
    moved = move.moved_piece
    captured = move.captured_piece
    if captured is not None:
        score += piece_value(captured.piece_type) * 16
        if moved is not None:
            score -= piece_value(moved.piece_type) * 2
        if captured.piece_type is PieceType.GENERAL:
            score += 1_000_000

    # Mild central preference helps move ordering in quiet positions.
    score -= abs(move.to_col - 4) * 2
    if side is Side.RED:
        score += (9 - move.to_row)
    else:
        score += move.to_row
    return score


def order_moves(moves: list[Move], side: Side) -> list[Move]:
    return sorted(moves, key=lambda m: _move_order_score(m, side), reverse=True)

