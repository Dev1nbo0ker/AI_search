from __future__ import annotations

import unittest

from cn_chess.core.board import Board
from cn_chess.core.enums import GameResult, PieceType, Side
from cn_chess.core.piece import Piece


def empty_board(side_to_move: Side = Side.RED) -> Board:
    board = Board()
    board.grid = [[None for _ in range(9)] for _ in range(10)]
    board.general_pos = {Side.RED: None, Side.BLACK: None}
    board.history.clear()
    board.side_to_move = side_to_move
    return board


def put(board: Board, row: int, col: int, piece_type: PieceType, side: Side) -> None:
    board.place_piece(row, col, Piece(piece_type, side))


def move_keys(board: Board, side: Side) -> set[tuple[int, int, int, int]]:
    return {move.key for move in board.generate_legal_moves(side)}


class XiangqiRulesTest(unittest.TestCase):
    def test_horse_leg_blocks_move(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)
        put(board, 0, 3, PieceType.GENERAL, Side.BLACK)
        put(board, 5, 4, PieceType.HORSE, Side.RED)
        put(board, 4, 4, PieceType.PAWN, Side.RED)

        self.assertNotIn((5, 4, 3, 3), move_keys(board, Side.RED))
        self.assertNotIn((5, 4, 3, 5), move_keys(board, Side.RED))

    def test_elephant_eye_blocks_move(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)
        put(board, 0, 3, PieceType.GENERAL, Side.BLACK)
        put(board, 9, 2, PieceType.ELEPHANT, Side.RED)
        put(board, 8, 3, PieceType.PAWN, Side.RED)

        self.assertNotIn((9, 2, 7, 4), move_keys(board, Side.RED))

    def test_cannon_requires_exactly_one_screen_to_capture(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)
        put(board, 0, 3, PieceType.GENERAL, Side.BLACK)
        put(board, 5, 0, PieceType.CANNON, Side.RED)
        put(board, 5, 2, PieceType.PAWN, Side.BLACK)

        self.assertNotIn((5, 0, 5, 2), move_keys(board, Side.RED))

        put(board, 5, 1, PieceType.PAWN, Side.RED)
        self.assertIn((5, 0, 5, 2), move_keys(board, Side.RED))

    def test_pawn_moves_sideways_only_after_crossing_river(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)
        put(board, 0, 3, PieceType.GENERAL, Side.BLACK)
        put(board, 6, 2, PieceType.PAWN, Side.RED)
        put(board, 4, 6, PieceType.PAWN, Side.RED)

        keys = move_keys(board, Side.RED)
        self.assertIn((6, 2, 5, 2), keys)
        self.assertNotIn((6, 2, 6, 1), keys)
        self.assertIn((4, 6, 4, 5), keys)
        self.assertIn((4, 6, 4, 7), keys)

    def test_general_cannot_leave_palace(self) -> None:
        board = empty_board()
        put(board, 9, 5, PieceType.GENERAL, Side.RED)
        put(board, 0, 3, PieceType.GENERAL, Side.BLACK)
        put(board, 5, 4, PieceType.PAWN, Side.RED)

        self.assertNotIn((9, 5, 9, 6), move_keys(board, Side.RED))
        self.assertIn((9, 5, 8, 5), move_keys(board, Side.RED))

    def test_move_cannot_expose_facing_generals(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)
        put(board, 0, 4, PieceType.GENERAL, Side.BLACK)
        put(board, 5, 4, PieceType.ROOK, Side.RED)

        self.assertNotIn((5, 4, 5, 3), move_keys(board, Side.RED))

    def test_board_reports_terminal_result(self) -> None:
        board = empty_board()
        put(board, 9, 4, PieceType.GENERAL, Side.RED)

        self.assertEqual(board.game_result(), GameResult.RED_WIN)


if __name__ == "__main__":
    unittest.main()
