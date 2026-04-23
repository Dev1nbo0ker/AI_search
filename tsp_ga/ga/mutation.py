from __future__ import annotations


def inversion_mutation(tour: list[int], start: int, end: int) -> list[int]:
    mutated = tour[:]
    mutated[start : end + 1] = reversed(mutated[start : end + 1])
    return mutated
