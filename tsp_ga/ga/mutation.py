from __future__ import annotations

import random


def inversion_mutation(tour: list[int], start: int, end: int) -> list[int]:
    mutated = tour[:]
    mutated[start : end + 1] = reversed(mutated[start : end + 1])
    return mutated


def swap_mutation(tour: list[int], rng: random.Random) -> list[int]:
    mutated = tour[:]
    i, j = rng.sample(range(len(tour)), 2)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def insertion_mutation(tour: list[int], rng: random.Random) -> list[int]:
    mutated = tour[:]
    index = rng.randrange(len(mutated))
    city = mutated.pop(index)
    mutated.insert(rng.randrange(len(mutated) + 1), city)
    return mutated


def displacement_mutation(tour: list[int], rng: random.Random) -> list[int]:
    mutated = tour[:]
    start = rng.randrange(len(mutated) - 1)
    end = rng.randrange(start + 1, len(mutated))
    segment = mutated[start : end + 1]
    del mutated[start : end + 1]
    insert_at = rng.randrange(len(mutated) + 1)
    return mutated[:insert_at] + segment + mutated[insert_at:]


def scramble_mutation(tour: list[int], rng: random.Random) -> list[int]:
    mutated = tour[:]
    start = rng.randrange(len(mutated) - 1)
    end = rng.randrange(start + 1, len(mutated))
    segment = mutated[start : end + 1]
    rng.shuffle(segment)
    mutated[start : end + 1] = segment
    return mutated


def adaptive_mutation(
    tour: list[int],
    generation: int,
    max_generation: int,
    rng: random.Random,
) -> list[int]:
    progress = generation / max_generation
    if progress < 0.3:
        return displacement_mutation(tour, rng) if rng.random() < 0.55 else scramble_mutation(tour, rng)
    if progress < 0.75:
        mutation = rng.choice(("inversion", "insertion", "swap"))
    else:
        mutation = rng.choice(("inversion", "insertion", "swap", "swap"))

    if mutation == "inversion":
        max_span = len(tour) if progress < 0.75 else min(len(tour), 8)
        start = rng.randrange(len(tour) - 1)
        end = rng.randrange(start + 1, min(len(tour), start + max_span))
        return inversion_mutation(tour, start, end)
    if mutation == "insertion":
        return insertion_mutation(tour, rng)
    return swap_mutation(tour, rng)
