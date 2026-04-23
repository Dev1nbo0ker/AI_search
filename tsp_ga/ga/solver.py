from __future__ import annotations

from dataclasses import replace
import random
import time

from tsp_ga.config import validate_config
from tsp_ga.core.distance import build_distance_matrix
from tsp_ga.ga.crossover import order_crossover
from tsp_ga.ga.fitness import evaluate_population
from tsp_ga.ga.initialization import initialize_population
from tsp_ga.ga.local_search import two_opt_local_search
from tsp_ga.ga.mutation import inversion_mutation
from tsp_ga.ga.replacement import next_generation, select_elites
from tsp_ga.ga.selection import tournament_select
from tsp_ga.models import ExperimentResult, GAConfig, GAResult, GenerationStats, TSPInstance


def run_ga(instance: TSPInstance, config: GAConfig) -> tuple[GAResult, list[GenerationStats]]:
    validate_config(config, instance.dimension)

    rng = random.Random(config.random_seed)
    distance_matrix = build_distance_matrix(instance.coordinates)
    population = initialize_population(config.population_size, instance.dimension, rng)

    best_route: list[int] = []
    best_distance = float("inf")
    history: list[GenerationStats] = []
    stagnant_generations = 0

    start_time = time.perf_counter()

    for generation in range(1, config.generations + 1):
        distances, fitnesses = evaluate_population(population, distance_matrix)

        generation_best_index = min(range(len(population)), key=lambda idx: distances[idx])
        generation_best_route = population[generation_best_index][:]
        generation_best_distance = distances[generation_best_index]

        if _should_run_two_opt(
            generation=generation,
            config=config,
            generation_best_distance=generation_best_distance,
            best_distance=best_distance,
            stagnant_generations=stagnant_generations,
        ):
            improved_route, improved_distance = two_opt_local_search(generation_best_route, distance_matrix)
            if config.validate_permutations:
                _validate_permutation(improved_route, instance.dimension, "2-opt")
            if improved_distance < distances[generation_best_index]:
                population[generation_best_index] = improved_route
                distances[generation_best_index] = improved_distance
                fitnesses[generation_best_index] = 1.0 / (improved_distance + 1e-12)
                generation_best_route = improved_route
                generation_best_distance = improved_distance

        generation_average = sum(distances) / len(distances)

        history.append(
            GenerationStats(
                generation=generation,
                best_distance=generation_best_distance,
                average_distance=generation_average,
            )
        )

        if generation_best_distance < best_distance:
            best_distance = generation_best_distance
            best_route = generation_best_route
            stagnant_generations = 0
        else:
            stagnant_generations += 1

        elites = select_elites(population, distances, config.elite_size)
        offspring = _create_offspring(
            population=population,
            fitnesses=fitnesses,
            config=config,
            rng=rng,
        )
        population = next_generation(elites, offspring, config.population_size)

    runtime = time.perf_counter() - start_time
    labeled_route = [instance.node_ids[index] for index in best_route]

    result = GAResult(
        seed=config.random_seed,
        best_route=labeled_route,
        best_distance=int(best_distance),
        generation_best=[item.best_distance for item in history],
        runtime_seconds=runtime,
    )
    return result, history


def run_multiple_seeds(
    instance: TSPInstance,
    config: GAConfig,
    seeds: list[int],
) -> tuple[ExperimentResult, list[GenerationStats]]:
    if not seeds:
        raise ValueError("At least one random seed is required.")

    run_results: list[GAResult] = []
    best_history: list[GenerationStats] = []
    best_distance = float("inf")
    total_runtime = 0.0

    for seed in seeds:
        run_config = replace(config, random_seed=seed)
        result, history = run_ga(instance, run_config)
        run_results.append(result)
        total_runtime += result.runtime_seconds

        if result.best_distance < best_distance:
            best_distance = result.best_distance
            best_history = history

    best_run = min(run_results, key=lambda item: item.best_distance)
    distances = [item.best_distance for item in run_results]
    summary = ExperimentResult(
        runs=run_results,
        best_run=best_run,
        mean_distance=sum(distances) / len(distances),
        worst_distance=max(distances),
        total_runtime_seconds=total_runtime,
    )
    return summary, best_history


def _create_offspring(
    population: list[list[int]],
    fitnesses: list[float],
    config: GAConfig,
    rng: random.Random,
) -> list[list[int]]:
    offspring: list[list[int]] = []
    target_size = config.population_size - config.elite_size
    num_cities = len(population[0])

    while len(offspring) < target_size:
        parent1 = tournament_select(population, fitnesses, config.tournament_size, rng)
        parent2 = tournament_select(population, fitnesses, config.tournament_size, rng)

        child1 = parent1[:]
        child2 = parent2[:]

        if rng.random() < config.crossover_rate:
            start, end = _random_segment(num_cities, rng)
            child1, child2 = order_crossover(parent1, parent2, start, end)
            if config.validate_permutations:
                _validate_permutation(child1, num_cities, "crossover")
                _validate_permutation(child2, num_cities, "crossover")

        if rng.random() < config.mutation_rate:
            start, end = _random_segment(num_cities, rng)
            child1 = inversion_mutation(child1, start, end)
            if config.validate_permutations:
                _validate_permutation(child1, num_cities, "mutation")

        if rng.random() < config.mutation_rate:
            start, end = _random_segment(num_cities, rng)
            child2 = inversion_mutation(child2, start, end)
            if config.validate_permutations:
                _validate_permutation(child2, num_cities, "mutation")

        offspring.append(child1)
        if len(offspring) < target_size:
            offspring.append(child2)

    return offspring


def _should_run_two_opt(
    generation: int,
    config: GAConfig,
    generation_best_distance: int,
    best_distance: float,
    stagnant_generations: int,
) -> bool:
    if not config.use_two_opt:
        return False
    if generation_best_distance < best_distance:
        return True
    if stagnant_generations >= config.two_opt_stagnation:
        return True
    return generation % config.two_opt_interval == 0


def _random_segment(num_cities: int, rng: random.Random) -> tuple[int, int]:
    start = rng.randrange(num_cities)
    end = rng.randrange(num_cities - 1)
    if end >= start:
        end += 1
    if start > end:
        start, end = end, start
    return start, end


def _validate_permutation(tour: list[int], num_cities: int, stage: str) -> None:
    if len(tour) != num_cities:
        raise ValueError(f"Invalid chromosome after {stage}: expected length {num_cities}, got {len(tour)}.")
    seen = [False] * num_cities
    for city in tour:
        if city < 0 or city >= num_cities or seen[city]:
            raise ValueError(f"Invalid chromosome after {stage}: each city must appear exactly once.")
        seen[city] = True
