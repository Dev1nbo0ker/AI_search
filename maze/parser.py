from __future__ import annotations

from .models import MazeProblem, Pos


def parse_maze(lines: list[str]) -> MazeProblem:
    """Parse and validate maze text."""
    cleaned: list[list[str]] = []
    allowed = {"S", "E", "0", "1"}

    for raw in lines:
        row = [ch for ch in raw.strip().replace(" ", "")]
        if row:
            cleaned.append(row)

    if not cleaned:
        raise ValueError("Maze cannot be empty.")

    cols = len(cleaned[0])
    for row in cleaned:
        if len(row) != cols:
            raise ValueError("Maze must be rectangular.")
        for ch in row:
            if ch not in allowed:
                raise ValueError(f"Invalid maze character: {ch}")

    start_positions: list[Pos] = []
    end_positions: list[Pos] = []
    for r, row in enumerate(cleaned):
        for c, ch in enumerate(row):
            if ch == "S":
                start_positions.append((r, c))
            elif ch == "E":
                end_positions.append((r, c))

    if len(start_positions) != 1 or len(end_positions) != 1:
        raise ValueError("Maze must contain exactly one S and one E.")

    return MazeProblem(
        grid=cleaned,
        start=start_positions[0],
        end=end_positions[0],
        rows=len(cleaned),
        cols=cols,
    )
