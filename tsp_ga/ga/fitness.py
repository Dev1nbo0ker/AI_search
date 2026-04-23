from __future__ import annotations

from tsp_ga.core.distance import tour_length


def distance_of(tour: list[int], distance_matrix: list[list[int]]) -> int:
    return tour_length(tour, distance_matrix)


def fitness_of(tour: list[int], distance_matrix: list[list[int]]) -> float:
    distance = distance_of(tour, distance_matrix)
    return 1.0 / (distance + 1e-12)


def evaluate_population(
    population: list[list[int]],
    distance_matrix: list[list[int]],
) -> tuple[list[int], list[float]]:
    distances = [distance_of(individual, distance_matrix) for individual in population]
    fitnesses = [1.0 / (distance + 1e-12) for distance in distances]
    return distances, fitnesses

