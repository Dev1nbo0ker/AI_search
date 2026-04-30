from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import PieceType, Side

if TYPE_CHECKING:
    from .board import Board
    from .piece import Piece


def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < 10 and 0 <= col < 9


def in_palace(side: Side, row: int, col: int) -> bool:
    if col < 3 or col > 5:
        return False
    if side is Side.RED:
        return 7 <= row <= 9
    return 0 <= row <= 2


def crossed_river(side: Side, row: int) -> bool:
    if side is Side.RED:
        return row <= 4
    return row >= 5


def path_clear_straight(board: "Board", r1: int, c1: int, r2: int, c2: int) -> bool:
    if r1 == r2:
        start, end = sorted((c1, c2))
        for c in range(start + 1, end):
            if board.piece_at(r1, c) is not None:
                return False
        return True
    if c1 == c2:
        start, end = sorted((r1, r2))
        for r in range(start + 1, end):
            if board.piece_at(r, c1) is not None:
                return False
        return True
    return False


def count_between_straight(board: "Board", r1: int, c1: int, r2: int, c2: int) -> int:
    if r1 == r2:
        start, end = sorted((c1, c2))
        return sum(1 for c in range(start + 1, end) if board.piece_at(r1, c) is not None)
    if c1 == c2:
        start, end = sorted((r1, r2))
        return sum(1 for r in range(start + 1, end) if board.piece_at(r, c1) is not None)
    return -1


def _append_if_enemy_or_empty(board: "Board", piece: "Piece", moves: list[tuple[int, int]], nr: int, nc: int) -> None:
    if not in_bounds(nr, nc):
        return
    target = board.piece_at(nr, nc)
    if target is None or target.side is not piece.side:
        moves.append((nr, nc))


def generate_piece_moves(board: "Board", row: int, col: int, piece: "Piece") -> list[tuple[int, int]]:
    moves: list[tuple[int, int]] = []
    side = piece.side
    kind = piece.piece_type

    if kind is PieceType.GENERAL:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            if in_bounds(nr, nc) and in_palace(side, nr, nc):
                _append_if_enemy_or_empty(board, piece, moves, nr, nc)

        # Flying general capture.
        enemy_general = board.general_pos.get(side.opponent)
        if enemy_general and enemy_general[1] == col and path_clear_straight(board, row, col, enemy_general[0], enemy_general[1]):
            moves.append(enemy_general)

    elif kind is PieceType.ADVISOR:
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nr, nc = row + dr, col + dc
            if in_bounds(nr, nc) and in_palace(side, nr, nc):
                _append_if_enemy_or_empty(board, piece, moves, nr, nc)

    elif kind is PieceType.ELEPHANT:
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            nr, nc = row + dr, col + dc
            eye_r, eye_c = row + dr // 2, col + dc // 2
            if not in_bounds(nr, nc):
                continue
            if side is Side.RED and nr < 5:
                continue
            if side is Side.BLACK and nr > 4:
                continue
            if board.piece_at(eye_r, eye_c) is not None:
                continue
            _append_if_enemy_or_empty(board, piece, moves, nr, nc)

    elif kind is PieceType.HORSE:
        horse_steps = (
            ((-1, 0), (-2, -1)),
            ((-1, 0), (-2, 1)),
            ((1, 0), (2, -1)),
            ((1, 0), (2, 1)),
            ((0, -1), (-1, -2)),
            ((0, -1), (1, -2)),
            ((0, 1), (-1, 2)),
            ((0, 1), (1, 2)),
        )
        for (leg_dr, leg_dc), (dr, dc) in horse_steps:
            leg_r, leg_c = row + leg_dr, col + leg_dc
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc):
                continue
            if board.piece_at(leg_r, leg_c) is not None:
                continue
            _append_if_enemy_or_empty(board, piece, moves, nr, nc)

    elif kind is PieceType.ROOK:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            while in_bounds(nr, nc):
                target = board.piece_at(nr, nc)
                if target is None:
                    moves.append((nr, nc))
                else:
                    if target.side is not side:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc

    elif kind is PieceType.CANNON:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            jumped = False
            while in_bounds(nr, nc):
                target = board.piece_at(nr, nc)
                if not jumped:
                    if target is None:
                        moves.append((nr, nc))
                    else:
                        jumped = True
                else:
                    if target is not None:
                        if target.side is not side:
                            moves.append((nr, nc))
                        break
                nr += dr
                nc += dc

    elif kind is PieceType.PAWN:
        forward_r = row + side.forward
        if in_bounds(forward_r, col):
            _append_if_enemy_or_empty(board, piece, moves, forward_r, col)

        if crossed_river(side, row):
            for dc in (-1, 1):
                nr, nc = row, col + dc
                if in_bounds(nr, nc):
                    _append_if_enemy_or_empty(board, piece, moves, nr, nc)

    return moves


def can_piece_attack(board: "Board", row: int, col: int, piece: "Piece", target_row: int, target_col: int) -> bool:
    side = piece.side
    kind = piece.piece_type

    if kind is PieceType.GENERAL:
        if abs(row - target_row) + abs(col - target_col) == 1 and in_palace(side, target_row, target_col):
            return True
        enemy_general = board.general_pos.get(side.opponent)
        if enemy_general and enemy_general == (target_row, target_col) and col == target_col:
            return path_clear_straight(board, row, col, target_row, target_col)
        return False

    if kind is PieceType.ADVISOR:
        return in_palace(side, target_row, target_col) and abs(row - target_row) == 1 and abs(col - target_col) == 1

    if kind is PieceType.ELEPHANT:
        if abs(row - target_row) != 2 or abs(col - target_col) != 2:
            return False
        if side is Side.RED and target_row < 5:
            return False
        if side is Side.BLACK and target_row > 4:
            return False
        eye_r, eye_c = (row + target_row) // 2, (col + target_col) // 2
        return board.piece_at(eye_r, eye_c) is None

    if kind is PieceType.HORSE:
        dr, dc = target_row - row, target_col - col
        if (abs(dr), abs(dc)) not in ((2, 1), (1, 2)):
            return False
        if abs(dr) == 2:
            leg_r, leg_c = row + dr // 2, col
        else:
            leg_r, leg_c = row, col + dc // 2
        return board.piece_at(leg_r, leg_c) is None

    if kind is PieceType.ROOK:
        if row != target_row and col != target_col:
            return False
        return path_clear_straight(board, row, col, target_row, target_col)

    if kind is PieceType.CANNON:
        if row != target_row and col != target_col:
            return False
        return count_between_straight(board, row, col, target_row, target_col) == 1

    if kind is PieceType.PAWN:
        dr, dc = target_row - row, target_col - col
        if dr == side.forward and dc == 0:
            return True
        return crossed_river(side, row) and dr == 0 and abs(dc) == 1

    return False

