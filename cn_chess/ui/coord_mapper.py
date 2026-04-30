from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CoordMapper:
    cell_size: int = 64
    margin: int = 40

    @property
    def board_width(self) -> int:
        return self.margin * 2 + self.cell_size * 8

    @property
    def board_height(self) -> int:
        return self.margin * 2 + self.cell_size * 9

    def board_to_screen(self, row: int, col: int, flip: bool = False) -> tuple[int, int]:
        if flip:
            row = 9 - row
            col = 8 - col
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return x, y

    def screen_to_board(self, x: int, y: int, flip: bool = False) -> Optional[tuple[int, int]]:
        rx = (x - self.margin) / self.cell_size
        ry = (y - self.margin) / self.cell_size
        col = round(rx)
        row = round(ry)
        if not (0 <= row < 10 and 0 <= col < 9):
            return None

        # Require click near an intersection point.
        sx = self.margin + col * self.cell_size
        sy = self.margin + row * self.cell_size
        max_dist = self.cell_size * 0.45
        if abs(x - sx) > max_dist or abs(y - sy) > max_dist:
            return None

        if flip:
            row = 9 - row
            col = 8 - col
        return row, col

