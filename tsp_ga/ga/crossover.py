from __future__ import annotations

import random


def order_crossover(parent1: list[int], parent2: list[int], start: int, end: int) -> tuple[list[int], list[int]]:
    return _build_child(parent1, parent2, start, end), _build_child(parent2, parent1, start, end)


def _build_child(base_parent: list[int], fill_parent: list[int], start: int, end: int) -> list[int]:
    size = len(base_parent)
    child = [-1] * size
    used = [False] * size

    for position in range(start, end + 1):
        city = base_parent[position]
        child[position] = city
        used[city] = True

    fill_positions = list(range(end + 1, size)) + list(range(0, start))
    fill_position_index = 0

    for offset in range(size):
        city = fill_parent[(end + 1 + offset) % size]
        if used[city]:
            continue
        child[fill_positions[fill_position_index]] = city
        used[city] = True
        fill_position_index += 1
        if fill_position_index == len(fill_positions):
            break

    return child


def sequential_constructive_crossover(
    parent1: list[int],
    parent2: list[int],
    distance_matrix: list[list[int]],
    rng: random.Random,
) -> list[int]:
    """Build a child by repeatedly choosing the shorter parent-successor edge."""
    size = len(parent1)
    positions1 = {city: index for index, city in enumerate(parent1)}
    positions2 = {city: index for index, city in enumerate(parent2)}
    current = rng.choice((parent1[0], parent2[0]))
    child = [current]
    used = {current}

    while len(child) < size:
        candidates: list[int] = []
        for parent, positions in ((parent1, positions1), (parent2, positions2)):
            successor = parent[(positions[current] + 1) % size]
            if successor not in used:
                candidates.append(successor)

        if candidates:
            current = min(candidates, key=lambda city: distance_matrix[child[-1]][city])
        else:
            current = min(
                (city for city in range(size) if city not in used),
                key=lambda city: distance_matrix[child[-1]][city],
            )

        child.append(current)
        used.add(current)

    return child
