from __future__ import annotations

import random

import numpy as np


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
    distance_matrix: np.ndarray,
    rng: random.Random,
) -> list[int]:
    """Build a child by repeatedly choosing the shorter parent-successor edge."""
    size = len(parent1)
    positions1 = [0] * size
    positions2 = [0] * size
    for index, city in enumerate(parent1):
        positions1[city] = index
    for index, city in enumerate(parent2):
        positions2[city] = index

    current = rng.choice((parent1[0], parent2[0]))
    child = [current]
    used = [False] * size
    used[current] = True

    while len(child) < size:
        candidate1 = parent1[(positions1[current] + 1) % size]
        candidate2 = parent2[(positions2[current] + 1) % size]

        if not used[candidate1] and not used[candidate2]:
            current_row = distance_matrix[current]
            if candidate1 == candidate2 or current_row[candidate1] <= current_row[candidate2]:
                current = candidate1
            else:
                current = candidate2
        elif not used[candidate1]:
            current = candidate1
        elif not used[candidate2]:
            current = candidate2
        else:
            current_row = distance_matrix[current]
            best_city = -1
            best_distance = None
            for city in range(size):
                if used[city]:
                    continue
                city_distance = current_row[city]
                if best_distance is None or city_distance < best_distance:
                    best_distance = city_distance
                    best_city = city
            current = best_city

        child.append(current)
        used[current] = True

    return child
