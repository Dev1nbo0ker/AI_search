from __future__ import annotations

from .types import State


def _matrix_to_state(matrix: list[list[int]]) -> State:
    return tuple(cell for row in matrix for cell in row)


def default_cases() -> list[tuple[str, State]]:
    return [
        (
            "Test Case 1",
            _matrix_to_state(
                [
                    [1, 2, 4, 8],
                    [5, 7, 11, 10],
                    [13, 15, 0, 3],
                    [14, 6, 9, 12],
                ]
            ),
        ),
        (
            "Test Case 2",
            _matrix_to_state(
                [
                    [14, 10, 6, 0],
                    [4, 9, 1, 8],
                    [2, 3, 5, 11],
                    [12, 13, 7, 15],
                ]
            ),
        ),
        (
            "Test Case 3",
            _matrix_to_state(
                [
                    [5, 1, 3, 4],
                    [2, 7, 8, 12],
                    [9, 6, 11, 15],
                    [0, 13, 10, 14],
                ]
            ),
        ),
        (
            "Test Case 4",
            _matrix_to_state(
                [
                    [6, 10, 3, 15],
                    [14, 8, 7, 11],
                    [5, 1, 0, 2],
                    [13, 12, 9, 4],
                ]
            ),
        ),
        (
            "Test Case 5",
            _matrix_to_state(
                [
                    [11, 3, 1, 7],
                    [4, 6, 8, 2],
                    [15, 9, 10, 13],
                    [14, 12, 5, 0],
                ]
            ),
        ),
        (
            "Test Case 6",
            _matrix_to_state(
                [
                    [0, 5, 15, 14],
                    [7, 9, 6, 13],
                    [1, 2, 12, 10],
                    [8, 11, 4, 3],
                ]
            ),
        ),
    ]
