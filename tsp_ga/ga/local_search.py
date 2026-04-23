from __future__ import annotations

from tsp_ga.core.distance import tour_length


def two_opt_local_search(tour: list[int], distance_matrix: list[list[int]]) -> tuple[list[int], int]:
    """Improve a tour using iterative 2-opt until no further improvement exists."""

    best_tour = tour[:]
    best_distance = tour_length(best_tour, distance_matrix)
    num_cities = len(best_tour)

    if num_cities < 4:
        return best_tour, best_distance

    improved = True
    while improved:
        improved = False
        for start in range(num_cities - 1):
            previous_city = best_tour[start - 1]
            current_city = best_tour[start]

            for end in range(start + 1, num_cities):
                if start == 0 and end == num_cities - 1:
                    continue

                next_city = best_tour[(end + 1) % num_cities]
                end_city = best_tour[end]

                old_cost = (
                    distance_matrix[previous_city][current_city]
                    + distance_matrix[end_city][next_city]
                )
                new_cost = (
                    distance_matrix[previous_city][end_city]
                    + distance_matrix[current_city][next_city]
                )

                if new_cost < old_cost:
                    best_tour[start : end + 1] = reversed(best_tour[start : end + 1])
                    best_distance += new_cost - old_cost
                    improved = True
                    break

            if improved:
                break

    return best_tour, best_distance
