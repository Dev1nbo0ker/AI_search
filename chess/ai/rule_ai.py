from __future__ import annotations

import random
from typing import Optional

from chess.core.board import Board
from chess.core.enums import Side
from chess.core.move import Move

from .base_ai import BaseAI
from .evaluator import piece_value


class RuleAI(BaseAI):
    """
    Rule-based AI:
    1) Prefer captures
    2) Prefer checking moves
    3) Avoid obvious blunders (moving high-value piece to attacked square)
    """

    def choose_move(self, board: Board, side: Side) -> Optional[Move]:
        legal_moves = board.generate_legal_moves(side)
        if not legal_moves:
            return None

        best_score = -10**18
        best_moves: list[Move] = []

        for move in legal_moves:
            score = self._score_move(board, move, side)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves)

    def _score_move(self, board: Board, move: Move, side: Side) -> int:
        moved_piece = move.moved_piece
        captured_piece = move.captured_piece
        score = 0

        # Priority 1: capture.
        if captured_piece is not None:
            score += 1000 + piece_value(captured_piece.piece_type) * 8
            if moved_piece is not None:
                score -= piece_value(moved_piece.piece_type) * 2

        undo = board.make_move(move)

        # Priority 2: check.
        if board.is_in_check(side.opponent):
            score += 900
            move.is_check = True

        # Priority 3: avoid obvious hanging.
        moved_piece_after = move.moved_piece
        if moved_piece_after is not None:
            attacked = board.is_square_attacked(move.to_row, move.to_col, side.opponent)
            defended = board.is_square_attacked(move.to_row, move.to_col, side)
            if attacked:
                penalty = piece_value(moved_piece_after.piece_type)
                if not defended:
                    penalty += piece_value(moved_piece_after.piece_type) // 2
                if captured_piece is not None and piece_value(captured_piece.piece_type) >= piece_value(moved_piece_after.piece_type):
                    penalty //= 3
                score -= penalty
            else:
                score += 30

        # Tiny bonus: improve forward development.
        if side is Side.RED:
            score += (9 - move.to_row)
        else:
            score += move.to_row

        board.unmake_move(undo)
        return score

