from __future__ import annotations

import random


def tournament_select(
    population: list[list[int]],
    fitnesses: list[float],
    tournament_size: int,
    rng: random.Random,
) -> list[int]:
    candidate_indices = rng.sample(range(len(population)), tournament_size)
    best_index = max(candidate_indices, key=lambda idx: fitnesses[idx])
    return population[best_index]
