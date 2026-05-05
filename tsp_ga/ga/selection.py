from __future__ import annotations

import random

import numpy as np


def tournament_select(
    population: list[list[int]],
    fitnesses: np.ndarray,
    tournament_size: int,
    rng: random.Random,
) -> list[int]:
    population_size = len(population)
    candidate_indices: list[int] = []
    seen: set[int] = set()

    while len(candidate_indices) < tournament_size:
        index = rng.randrange(population_size)
        if index in seen:
            continue
        seen.add(index)
        candidate_indices.append(index)

    best_index = candidate_indices[0]
    best_fitness = fitnesses[best_index]
    for index in candidate_indices[1:]:
        if fitnesses[index] > best_fitness:
            best_index = index
            best_fitness = fitnesses[index]
    return population[best_index]
