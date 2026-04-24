from __future__ import annotations

import random

from tsp_ga.core.distance import tour_length


def create_random_individual(num_cities: int, rng: random.Random) -> list[int]:
    individual = list(range(num_cities))
    rng.shuffle(individual)
    return individual


def create_nearest_neighbor_individual(
    num_cities: int,
    distance_matrix: list[list[int]],
    rng: random.Random,
    start_city: int | None = None,
) -> list[int]:
    current = rng.randrange(num_cities) if start_city is None else start_city
    tour = [current]
    unvisited = set(range(num_cities))
    unvisited.remove(current)

    while unvisited:
        current = min(unvisited, key=lambda city: distance_matrix[current][city])
        tour.append(current)
        unvisited.remove(current)

    return tour


def create_randomized_greedy_individual(
    num_cities: int,
    distance_matrix: list[list[int]],
    rng: random.Random,
    candidate_count: int = 4,
) -> list[int]:
    current = rng.randrange(num_cities)
    tour = [current]
    unvisited = set(range(num_cities))
    unvisited.remove(current)

    while unvisited:
        candidates = sorted(unvisited, key=lambda city: distance_matrix[current][city])
        current = rng.choice(candidates[: min(candidate_count, len(candidates))])
        tour.append(current)
        unvisited.remove(current)

    return tour


def initialize_population(
    population_size: int,
    num_cities: int,
    rng: random.Random,
    distance_matrix: list[list[int]] | None = None,
    greedy_fraction: float = 0.0,
    randomized_greedy_fraction: float = 0.0,
) -> list[list[int]]:
    if distance_matrix is None:
        return [create_random_individual(num_cities, rng) for _ in range(population_size)]

    population: list[list[int]] = []
    greedy_count = int(population_size * greedy_fraction)
    randomized_count = int(population_size * randomized_greedy_fraction)

    starts = list(range(num_cities))
    rng.shuffle(starts)
    for start_city in starts[:greedy_count]:
        population.append(create_nearest_neighbor_individual(num_cities, distance_matrix, rng, start_city))

    while len(population) < greedy_count + randomized_count:
        population.append(create_randomized_greedy_individual(num_cities, distance_matrix, rng))

    while len(population) < population_size:
        population.append(create_random_individual(num_cities, rng))

    population.sort(key=lambda tour: tour_length(tour, distance_matrix))
    return population[:population_size]

