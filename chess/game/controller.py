from __future__ import annotations

import pygame

from chess.core.board import Board
from chess.core.enums import GameResult, Side
from chess.core.move import Move
from chess.game.config import GameConfig
from chess.game.players import Player, create_player
from chess.ui.coord_mapper import CoordMapper
from chess.ui.pygame_view import PygameView


class GameController:
    def __init__(self, config: GameConfig) -> None:
        pygame.init()
        self.config = config
        self.board = Board()
        self.mapper = CoordMapper()
        self.view = PygameView(self.mapper, flip_view=config.flip_view)
        self.clock = pygame.time.Clock()

        self.players: dict[Side, Player] = {
            Side.RED: create_player(Side.RED, config.red_control, config.red_depth),
            Side.BLACK: create_player(Side.BLACK, config.black_control, config.black_depth),
        }

        self.running = True
        self.result = GameResult.ONGOING
        self.selected: tuple[int, int] | None = None
        self.last_ai_move_ms = 0

    def run(self) -> None:
        while self.running:
            self._handle_events()
            if self.result is GameResult.ONGOING:
                self._maybe_make_ai_move()
                self._update_result()

            legal_targets = self._selected_targets() if self.result is GameResult.ONGOING else set()
            self.view.draw(
                board=self.board,
                selected=self.selected,
                legal_targets=legal_targets,
                status_text=self._status_text(),
            )
            self.clock.tick(self.config.fps)

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.result is not GameResult.ONGOING:
                    continue
                side = self.board.side_to_move
                player = self.players[side]
                if player.is_human:
                    self._handle_human_click(event.pos)

    def _handle_human_click(self, pos: tuple[int, int]) -> None:
        side = self.board.side_to_move
        board_pos = self.mapper.screen_to_board(pos[0], pos[1], flip=self.config.flip_view)
        if board_pos is None:
            return

        row, col = board_pos
        piece = self.board.piece_at(row, col)
        legal_moves = self.board.generate_legal_moves(side)

        if self.selected is None:
            if piece is not None and piece.side is side:
                self.selected = (row, col)
            return

        selected_row, selected_col = self.selected
        for move in legal_moves:
            if (
                move.from_row == selected_row
                and move.from_col == selected_col
                and move.to_row == row
                and move.to_col == col
            ):
                self.board.make_move(move)
                self.selected = None
                return

        if piece is not None and piece.side is side:
            self.selected = (row, col)
        else:
            self.selected = None

    def _selected_targets(self) -> set[tuple[int, int]]:
        if self.selected is None:
            return set()
        side = self.board.side_to_move
        sr, sc = self.selected
        targets: set[tuple[int, int]] = set()
        for move in self.board.generate_legal_moves(side):
            if move.from_row == sr and move.from_col == sc:
                targets.add((move.to_row, move.to_col))
        return targets

    def _maybe_make_ai_move(self) -> None:
        side = self.board.side_to_move
        player = self.players[side]
        if player.is_human:
            return

        now = pygame.time.get_ticks()
        if now - self.last_ai_move_ms < self.config.ai_move_delay_ms:
            return

        move = player.choose_move(self.board)
        if move is not None:
            self.board.make_move(move)
            self.selected = None
            self.last_ai_move_ms = now

    def _update_result(self) -> None:
        if not self.board.has_general(Side.RED):
            self.result = GameResult.BLACK_WIN
            return
        if not self.board.has_general(Side.BLACK):
            self.result = GameResult.RED_WIN
            return

        side = self.board.side_to_move
        legal_moves = self.board.generate_legal_moves(side)
        if legal_moves:
            self.result = GameResult.ONGOING
            return

        if self.board.is_in_check(side):
            self.result = GameResult.BLACK_WIN if side is Side.RED else GameResult.RED_WIN
        else:
            self.result = GameResult.DRAW

    def _status_text(self) -> str:
        if self.result is GameResult.RED_WIN:
            return "红方胜利（将死）"
        if self.result is GameResult.BLACK_WIN:
            return "黑方胜利（将死）"
        if self.result is GameResult.DRAW:
            return "和棋（困毙）"

        side = self.board.side_to_move
        player = self.players[side]
        text = f"轮到{side.label}：{player.control_type.value}"
        if self.board.is_in_check(side):
            text += "（被将军）"
        return text

