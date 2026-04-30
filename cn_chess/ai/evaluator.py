from __future__ import annotations

from cn_chess.core.board import Board
from cn_chess.core.enums import PieceType, Side
from cn_chess.core.piece import Piece


PIECE_VALUES: dict[PieceType, int] = {
    PieceType.GENERAL: 10000,
    PieceType.ROOK: 600,
    PieceType.HORSE: 270,
    PieceType.CANNON: 300,
    PieceType.ELEPHANT: 120,
    PieceType.ADVISOR: 120,
    PieceType.PAWN: 70,
}

# Tables are in RED perspective (row 0 at top, row 9 at bottom).
ZERO_TABLE = [[0 for _ in range(9)] for _ in range(10)]
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 4, 6, 8, 8, 8, 6, 4, 2],
    [4, 6, 8, 10, 12, 10, 8, 6, 4],
    [6, 10, 12, 14, 16, 14, 12, 10, 6],
    [8, 12, 16, 20, 24, 20, 16, 12, 8],
    [10, 14, 18, 22, 26, 22, 18, 14, 10],
    [6, 10, 14, 18, 20, 18, 14, 10, 6],
    [2, 6, 8, 10, 12, 10, 8, 6, 2],
    [0, 2, 4, 6, 8, 6, 4, 2, 0],
]
HORSE_TABLE = [
    [4, 8, 10, 10, 10, 10, 10, 8, 4],
    [6, 10, 12, 14, 14, 14, 12, 10, 6],
    [8, 12, 16, 18, 18, 18, 16, 12, 8],
    [10, 14, 18, 22, 22, 22, 18, 14, 10],
    [10, 16, 20, 24, 24, 24, 20, 16, 10],
    [10, 16, 20, 24, 24, 24, 20, 16, 10],
    [8, 14, 18, 22, 22, 22, 18, 14, 8],
    [6, 10, 14, 18, 18, 18, 14, 10, 6],
    [4, 8, 12, 14, 14, 14, 12, 8, 4],
    [2, 4, 8, 10, 10, 10, 8, 4, 2],
]
CANNON_TABLE = [
    [2, 4, 4, 6, 6, 6, 4, 4, 2],
    [4, 6, 8, 10, 10, 10, 8, 6, 4],
    [4, 8, 12, 14, 14, 14, 12, 8, 4],
    [6, 10, 14, 16, 18, 16, 14, 10, 6],
    [6, 10, 14, 18, 20, 18, 14, 10, 6],
    [6, 10, 14, 18, 20, 18, 14, 10, 6],
    [6, 10, 14, 16, 18, 16, 14, 10, 6],
    [4, 8, 12, 14, 14, 14, 12, 8, 4],
    [2, 6, 8, 10, 10, 10, 8, 6, 2],
    [0, 2, 4, 4, 6, 4, 4, 2, 0],
]
ROOK_TABLE = [
    [8, 8, 8, 10, 12, 10, 8, 8, 8],
    [10, 10, 10, 12, 14, 12, 10, 10, 10],
    [10, 10, 12, 14, 16, 14, 12, 10, 10],
    [12, 12, 12, 14, 18, 14, 12, 12, 12],
    [12, 14, 14, 16, 20, 16, 14, 14, 12],
    [12, 14, 14, 16, 20, 16, 14, 14, 12],
    [12, 12, 12, 14, 18, 14, 12, 12, 12],
    [10, 10, 12, 14, 16, 14, 12, 10, 10],
    [8, 8, 10, 12, 14, 12, 10, 8, 8],
    [6, 6, 8, 10, 12, 10, 8, 6, 6],
]

POSITION_TABLES: dict[PieceType, list[list[int]]] = {
    PieceType.GENERAL: ZERO_TABLE,
    PieceType.ADVISOR: ZERO_TABLE,
    PieceType.ELEPHANT: ZERO_TABLE,
    PieceType.HORSE: HORSE_TABLE,
    PieceType.ROOK: ROOK_TABLE,
    PieceType.CANNON: CANNON_TABLE,
    PieceType.PAWN: PAWN_TABLE,
}


def piece_value(piece_type: PieceType) -> int:
    return PIECE_VALUES[piece_type]


def _position_bonus(piece: Piece, row: int, col: int) -> int:
    table = POSITION_TABLES[piece.piece_type]
    if piece.side is Side.RED:
        return table[row][col]
    mirrored_row = 9 - row
    mirrored_col = 8 - col
    return table[mirrored_row][mirrored_col]


def evaluate(board: Board, side: Side) -> int:
    own_score = 0
    opp_score = 0

    for row, col, piece in board.iter_pieces():
        material = PIECE_VALUES[piece.piece_type]
        positional = _position_bonus(piece, row, col)
        pawn_cross = 0
        if piece.piece_type is PieceType.PAWN:
            if (piece.side is Side.RED and row <= 4) or (piece.side is Side.BLACK and row >= 5):
                pawn_cross = 30
        score = material + positional + pawn_cross

        if piece.side is side:
            own_score += score
        else:
            opp_score += score

    tactical_bonus = 0
    if board.is_in_check(side.opponent):
        tactical_bonus += 40
    if board.is_in_check(side):
        tactical_bonus -= 40

    return own_score - opp_score + tactical_bonus

