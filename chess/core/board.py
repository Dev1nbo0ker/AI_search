from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

from . import rules
from .enums import PieceType, Side
from .move import Move
from .piece import Piece


Position = tuple[int, int]


@dataclass
class UndoState:
    move: Move
    captured_piece: Optional[Piece]
    prev_general_pos: dict[Side, Optional[Position]]
    prev_side_to_move: Side


class Board:
    def __init__(self) -> None:
        self.grid: list[list[Optional[Piece]]] = [[None for _ in range(9)] for _ in range(10)]
        self.side_to_move: Side = Side.RED
        self.general_pos: dict[Side, Optional[Position]] = {Side.RED: None, Side.BLACK: None}
        self.history: list[UndoState] = []
        self.reset()

    def reset(self) -> None:
        self.grid = [[None for _ in range(9)] for _ in range(10)]
        self.side_to_move = Side.RED
        self.history.clear()
        self.general_pos = {Side.RED: None, Side.BLACK: None}

        back_rank = [
            PieceType.ROOK,
            PieceType.HORSE,
            PieceType.ELEPHANT,
            PieceType.ADVISOR,
            PieceType.GENERAL,
            PieceType.ADVISOR,
            PieceType.ELEPHANT,
            PieceType.HORSE,
            PieceType.ROOK,
        ]

        for c, kind in enumerate(back_rank):
            self.place_piece(0, c, Piece(kind, Side.BLACK))
            self.place_piece(9, c, Piece(kind, Side.RED))

        self.place_piece(2, 1, Piece(PieceType.CANNON, Side.BLACK))
        self.place_piece(2, 7, Piece(PieceType.CANNON, Side.BLACK))
        self.place_piece(7, 1, Piece(PieceType.CANNON, Side.RED))
        self.place_piece(7, 7, Piece(PieceType.CANNON, Side.RED))

        for c in (0, 2, 4, 6, 8):
            self.place_piece(3, c, Piece(PieceType.PAWN, Side.BLACK))
            self.place_piece(6, c, Piece(PieceType.PAWN, Side.RED))

    def place_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        self.grid[row][col] = piece
        if piece is not None and piece.piece_type is PieceType.GENERAL:
            self.general_pos[piece.side] = (row, col)

    def piece_at(self, row: int, col: int) -> Optional[Piece]:
        if not rules.in_bounds(row, col):
            return None
        return self.grid[row][col]

    def iter_pieces(self) -> Iterator[tuple[int, int, Piece]]:
        for r in range(10):
            for c in range(9):
                piece = self.grid[r][c]
                if piece is not None:
                    yield r, c, piece

    def generate_pseudo_legal_moves(self, side: Optional[Side] = None) -> list[Move]:
        side = side or self.side_to_move
        moves: list[Move] = []
        for r, c, piece in self.iter_pieces():
            if piece.side is not side:
                continue
            for nr, nc in rules.generate_piece_moves(self, r, c, piece):
                target = self.piece_at(nr, nc)
                if target is not None and target.side is side:
                    continue
                moves.append(
                    Move(
                        from_row=r,
                        from_col=c,
                        to_row=nr,
                        to_col=nc,
                        moved_piece=piece,
                        captured_piece=target,
                    )
                )
        return moves

    def generate_legal_moves(self, side: Optional[Side] = None) -> list[Move]:
        side = side or self.side_to_move
        legal_moves: list[Move] = []
        for move in self.generate_pseudo_legal_moves(side):
            undo = self.make_move(move)
            illegal = self.is_in_check(side) or self.is_generals_facing()
            self.unmake_move(undo)
            if not illegal:
                legal_moves.append(move)
        return legal_moves

    def make_move(self, move: Move) -> UndoState:
        fr, fc, tr, tc = move.from_row, move.from_col, move.to_row, move.to_col
        moving = self.piece_at(fr, fc)
        if moving is None:
            raise ValueError(f"No piece on source square: {(fr, fc)}")

        captured = self.piece_at(tr, tc)
        move.moved_piece = moving
        move.captured_piece = captured

        undo = UndoState(
            move=move,
            captured_piece=captured,
            prev_general_pos=self.general_pos.copy(),
            prev_side_to_move=self.side_to_move,
        )

        self.grid[tr][tc] = moving
        self.grid[fr][fc] = None

        if moving.piece_type is PieceType.GENERAL:
            self.general_pos[moving.side] = (tr, tc)
        if captured is not None and captured.piece_type is PieceType.GENERAL:
            self.general_pos[captured.side] = None

        self.side_to_move = self.side_to_move.opponent
        self.history.append(undo)
        return undo

    def unmake_move(self, undo: UndoState) -> None:
        move = undo.move
        fr, fc, tr, tc = move.from_row, move.from_col, move.to_row, move.to_col
        moved_piece = move.moved_piece
        if moved_piece is None:
            raise ValueError("Cannot unmake move without moved_piece")

        self.grid[fr][fc] = moved_piece
        self.grid[tr][tc] = undo.captured_piece
        self.general_pos = undo.prev_general_pos
        self.side_to_move = undo.prev_side_to_move

        if self.history and self.history[-1] is undo:
            self.history.pop()
        elif undo in self.history:
            self.history.remove(undo)

    def is_generals_facing(self) -> bool:
        red_pos = self.general_pos.get(Side.RED)
        black_pos = self.general_pos.get(Side.BLACK)
        if red_pos is None or black_pos is None:
            return False
        if red_pos[1] != black_pos[1]:
            return False
        return rules.path_clear_straight(self, red_pos[0], red_pos[1], black_pos[0], black_pos[1])

    def is_square_attacked(self, row: int, col: int, attacker_side: Side) -> bool:
        for r, c, piece in self.iter_pieces():
            if piece.side is not attacker_side:
                continue
            if rules.can_piece_attack(self, r, c, piece, row, col):
                return True
        return False

    def is_in_check(self, side: Side) -> bool:
        general = self.general_pos.get(side)
        if general is None:
            return True
        return self.is_square_attacked(general[0], general[1], side.opponent)

    def has_general(self, side: Side) -> bool:
        return self.general_pos.get(side) is not None

    def terminal_winner(self) -> Optional[Side]:
        if not self.has_general(Side.RED):
            return Side.BLACK
        if not self.has_general(Side.BLACK):
            return Side.RED

        side = self.side_to_move
        legal = self.generate_legal_moves(side)
        if legal:
            return None
        if self.is_in_check(side):
            return side.opponent
        return None

    def is_stalemate(self) -> bool:
        if not self.has_general(Side.RED) or not self.has_general(Side.BLACK):
            return False
        side = self.side_to_move
        legal = self.generate_legal_moves(side)
        return len(legal) == 0 and not self.is_in_check(side)

