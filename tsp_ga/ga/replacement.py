from __future__ import annotations

import numpy as np


def select_elites(
    population: list[list[int]],
    distances: np.ndarray,
    elite_size: int,
) -> list[list[int]]:
    if elite_size == 0:
        return []

    elite_indices = np.argpartition(distances, elite_size - 1)[:elite_size]
    elite_indices = elite_indices[np.argsort(distances[elite_indices])]
    return [population[int(index)][:] for index in elite_indices]


def next_generation(
    elites: list[list[int]],
    offspring: list[list[int]],
    population_size: int,
) -> list[list[int]]:
    combined = elites + offspring
    return combined[:population_size]
