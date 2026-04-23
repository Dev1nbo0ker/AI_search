from __future__ import annotations

import random


def create_random_individual(num_cities: int, rng: random.Random) -> list[int]:
    individual = list(range(num_cities))
    rng.shuffle(individual)
    return individual


def initialize_population(
    population_size: int,
    num_cities: int,
    rng: random.Random,
) -> list[list[int]]:
    return [create_random_individual(num_cities, rng) for _ in range(population_size)]

