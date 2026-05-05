from __future__ import annotations

import numpy as np

from tsp_ga.core.distance import batch_tour_lengths, tour_length


def distance_of(tour: list[int], distance_matrix: np.ndarray) -> int:
    return tour_length(tour, distance_matrix)


def fitness_of(tour: list[int], distance_matrix: np.ndarray) -> float:
    distance = distance_of(tour, distance_matrix)
    return 1.0 / (distance + 1e-12)


def evaluate_population(
    population: list[list[int]],
    distance_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    distances = batch_tour_lengths(population, distance_matrix)
    fitnesses = 1.0 / (distances.astype(np.float64) + 1e-12)
    return distances, fitnesses

