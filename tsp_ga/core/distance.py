from __future__ import annotations

import math

import numpy as np


def euclidean_distance(a: tuple[float, float], b: tuple[float, float]) -> int:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def build_distance_matrix(coordinates: list[tuple[float, float]]) -> np.ndarray:
    coords = np.asarray(coordinates, dtype=np.float64)
    deltas = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    squared = np.sum(deltas * deltas, axis=2)
    return np.rint(np.sqrt(squared)).astype(np.int32, copy=False)

def tour_length(tour: list[int], distance_matrix: np.ndarray) -> int:
    route = np.asarray(tour, dtype=np.intp)
    next_route = np.roll(route, -1)
    return int(distance_matrix[route, next_route].sum())


def batch_tour_lengths(population: list[list[int]], distance_matrix: np.ndarray) -> np.ndarray:
    routes = np.asarray(population, dtype=np.intp)
    next_routes = np.roll(routes, -1, axis=1)
    return distance_matrix[routes, next_routes].sum(axis=1, dtype=np.int64)


def tour_length_python(tour: list[int], distance_matrix: np.ndarray) -> int:
    total = 0
    num_cities = len(tour)

    for index in range(num_cities):
        current_city = tour[index]
        next_city = tour[(index + 1) % num_cities]
        total += distance_matrix[current_city][next_city]

    return int(total)
