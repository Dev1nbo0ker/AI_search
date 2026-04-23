from __future__ import annotations

import math


def euclidean_distance(a: tuple[float, float], b: tuple[float, float]) -> int:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def build_distance_matrix(coordinates: list[tuple[float, float]]) -> list[list[int]]:
    num_cities = len(coordinates)
    matrix = [[0] * num_cities for _ in range(num_cities)]

    for i in range(num_cities):
        for j in range(i + 1, num_cities):
            distance = euclidean_distance(coordinates[i], coordinates[j])
            matrix[i][j] = distance
            matrix[j][i] = distance

    return matrix


def tour_length(tour: list[int], distance_matrix: list[list[int]]) -> int:
    total = 0
    num_cities = len(tour)

    for index in range(num_cities):
        current_city = tour[index]
        next_city = tour[(index + 1) % num_cities]
        total += distance_matrix[current_city][next_city]

    return total

