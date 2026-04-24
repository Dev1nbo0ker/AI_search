from __future__ import annotations

from typing import Optional

from chess.core.board import Board
from chess.core.enums import Side
from chess.core.move import Move

from .base_ai import BaseAI
from .evaluator import evaluate
from .move_ordering import order_moves


MATE_SCORE = 1_000_000


class AlphaBetaAI(BaseAI):
    def __init__(self, depth: int = 3) -> None:
        self.depth = max(1, depth)

    def choose_move(self, board: Board, side: Side) -> Optional[Move]:
        legal_moves = board.generate_legal_moves(side)
        if not legal_moves:
            return None

        alpha = -MATE_SCORE
        beta = MATE_SCORE
        best_score = -MATE_SCORE
        best_move: Optional[Move] = None

        for move in order_moves(legal_moves, side):
            undo = board.make_move(move)
            score = -self._negamax(board, self.depth - 1, -beta, -alpha, side.opponent, ply=1)
            board.unmake_move(undo)

            if score > best_score:
                best_score = score
                best_move = move
            if score > alpha:
                alpha = score

        return best_move

    def _negamax(self, board: Board, depth: int, alpha: int, beta: int, side: Side, ply: int) -> int:
        if not board.has_general(side):
            return -MATE_SCORE + ply
        if not board.has_general(side.opponent):
            return MATE_SCORE - ply

        legal_moves = board.generate_legal_moves(side)
        if not legal_moves:
            if board.is_in_check(side):
                return -MATE_SCORE + ply
            return 0

        if depth == 0:
            return evaluate(board, side)

        best = -MATE_SCORE
        for move in order_moves(legal_moves, side):
            undo = board.make_move(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha, side.opponent, ply + 1)
            board.unmake_move(undo)

            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return best

