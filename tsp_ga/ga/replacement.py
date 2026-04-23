from __future__ import annotations


def select_elites(
    population: list[list[int]],
    distances: list[int],
    elite_size: int,
) -> list[list[int]]:
    if elite_size == 0:
        return []

    ranked_indices = sorted(range(len(population)), key=lambda idx: distances[idx])
    return [population[index][:] for index in ranked_indices[:elite_size]]


def next_generation(
    elites: list[list[int]],
    offspring: list[list[int]],
    population_size: int,
) -> list[list[int]]:
    combined = elites + offspring
    return combined[:population_size]

