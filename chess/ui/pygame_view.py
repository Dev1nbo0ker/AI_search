from __future__ import annotations

import pygame

from chess.core.board import Board
from chess.core.enums import PieceType, Side
from chess.ui.coord_mapper import CoordMapper


PIECE_TEXT = {
    (Side.RED, PieceType.GENERAL): "帅",
    (Side.RED, PieceType.ADVISOR): "仕",
    (Side.RED, PieceType.ELEPHANT): "相",
    (Side.RED, PieceType.HORSE): "马",
    (Side.RED, PieceType.ROOK): "车",
    (Side.RED, PieceType.CANNON): "炮",
    (Side.RED, PieceType.PAWN): "兵",
    (Side.BLACK, PieceType.GENERAL): "将",
    (Side.BLACK, PieceType.ADVISOR): "士",
    (Side.BLACK, PieceType.ELEPHANT): "象",
    (Side.BLACK, PieceType.HORSE): "马",
    (Side.BLACK, PieceType.ROOK): "车",
    (Side.BLACK, PieceType.CANNON): "炮",
    (Side.BLACK, PieceType.PAWN): "卒",
}


class PygameView:
    def __init__(self, mapper: CoordMapper, flip_view: bool = False) -> None:
        self.mapper = mapper
        self.flip_view = flip_view
        self.screen = pygame.display.set_mode((mapper.board_width, mapper.board_height + 70))
        pygame.display.set_caption("中国象棋")

        self.bg_color = (240, 210, 160)
        self.line_color = (60, 40, 20)
        self.red_color = (180, 35, 25)
        self.black_color = (30, 30, 30)
        self.select_color = (30, 140, 220)
        self.target_color = (30, 170, 90)

        self.piece_radius = mapper.cell_size // 2 - 5
        self.board_font = self._load_font(28)
        self.piece_font = self._load_font(34)
        self.status_font = self._load_font(26)

    @staticmethod
    def _load_font(size: int) -> pygame.font.Font:
        for name in ("Microsoft YaHei", "SimHei", "KaiTi", "Arial Unicode MS"):
            font = pygame.font.SysFont(name, size)
            if font is not None:
                return font
        return pygame.font.Font(None, size)

    def draw(
        self,
        board: Board,
        selected: tuple[int, int] | None,
        legal_targets: set[tuple[int, int]],
        status_text: str,
    ) -> None:
        self.screen.fill(self.bg_color)
        self._draw_board_grid()
        self._draw_markers(selected, legal_targets)
        self._draw_pieces(board)
        self._draw_status(status_text)
        pygame.display.flip()

    def _draw_board_grid(self) -> None:
        m = self.mapper
        # Horizontal lines.
        for r in range(10):
            y = m.margin + r * m.cell_size
            x1 = m.margin
            x2 = m.margin + 8 * m.cell_size
            pygame.draw.line(self.screen, self.line_color, (x1, y), (x2, y), 2)

        # Vertical lines with river gap for middle columns.
        for c in range(9):
            x = m.margin + c * m.cell_size
            y_top = m.margin
            y_river_top = m.margin + 4 * m.cell_size
            y_river_bottom = m.margin + 5 * m.cell_size
            y_bottom = m.margin + 9 * m.cell_size
            if c in (0, 8):
                pygame.draw.line(self.screen, self.line_color, (x, y_top), (x, y_bottom), 2)
            else:
                pygame.draw.line(self.screen, self.line_color, (x, y_top), (x, y_river_top), 2)
                pygame.draw.line(self.screen, self.line_color, (x, y_river_bottom), (x, y_bottom), 2)

        # Palaces.
        self._draw_line_board((0, 3), (2, 5))
        self._draw_line_board((0, 5), (2, 3))
        self._draw_line_board((7, 3), (9, 5))
        self._draw_line_board((7, 5), (9, 3))

        river_text = self.board_font.render("楚 河        汉 界", True, self.line_color)
        text_rect = river_text.get_rect(
            center=(m.margin + 4 * m.cell_size, m.margin + int(4.5 * m.cell_size))
        )
        self.screen.blit(river_text, text_rect)

    def _draw_line_board(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> None:
        x1, y1 = self.mapper.board_to_screen(from_pos[0], from_pos[1], self.flip_view)
        x2, y2 = self.mapper.board_to_screen(to_pos[0], to_pos[1], self.flip_view)
        pygame.draw.line(self.screen, self.line_color, (x1, y1), (x2, y2), 2)

    def _draw_markers(self, selected: tuple[int, int] | None, legal_targets: set[tuple[int, int]]) -> None:
        if selected is not None:
            sx, sy = self.mapper.board_to_screen(selected[0], selected[1], self.flip_view)
            pygame.draw.circle(self.screen, self.select_color, (sx, sy), self.piece_radius + 5, 3)

        for row, col in legal_targets:
            x, y = self.mapper.board_to_screen(row, col, self.flip_view)
            pygame.draw.circle(self.screen, self.target_color, (x, y), 8)

    def _draw_pieces(self, board: Board) -> None:
        for row, col, piece in board.iter_pieces():
            x, y = self.mapper.board_to_screen(row, col, self.flip_view)
            pygame.draw.circle(self.screen, (245, 225, 190), (x, y), self.piece_radius)
            pygame.draw.circle(self.screen, self.line_color, (x, y), self.piece_radius, 2)

            text = PIECE_TEXT[(piece.side, piece.piece_type)]
            color = self.red_color if piece.side is Side.RED else self.black_color
            text_img = self.piece_font.render(text, True, color)
            text_rect = text_img.get_rect(center=(x, y - 1))
            self.screen.blit(text_img, text_rect)

    def _draw_status(self, status_text: str) -> None:
        h = self.mapper.board_height
        pygame.draw.rect(self.screen, (225, 190, 140), (0, h, self.mapper.board_width, 70))
        text_img = self.status_font.render(status_text, True, (20, 20, 20))
        self.screen.blit(text_img, (20, h + 18))

