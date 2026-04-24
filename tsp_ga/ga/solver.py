from __future__ import annotations

from dataclasses import replace
import random
import time

from tsp_ga.config import validate_config
from tsp_ga.core.distance import build_distance_matrix
from tsp_ga.ga.crossover import order_crossover, sequential_constructive_crossover
from tsp_ga.ga.fitness import evaluate_population
from tsp_ga.ga.initialization import initialize_population
from tsp_ga.ga.local_search import two_opt_local_search
from tsp_ga.ga.mutation import adaptive_mutation
from tsp_ga.ga.replacement import next_generation, select_elites
from tsp_ga.ga.selection import tournament_select
from tsp_ga.models import ExperimentResult, GAConfig, GAResult, GenerationStats, TSPInstance


def run_ga(instance: TSPInstance, config: GAConfig) -> tuple[GAResult, list[GenerationStats]]:
    validate_config(config, instance.dimension)

    rng = random.Random(config.random_seed)
    distance_matrix = build_distance_matrix(instance.coordinates)
    population = initialize_population(
        config.population_size,
        instance.dimension,
        rng,
        distance_matrix=distance_matrix,
        greedy_fraction=config.greedy_initial_fraction,
        randomized_greedy_fraction=config.randomized_greedy_initial_fraction,
    )

    best_route: list[int] = []
    best_distance = float("inf")
    history: list[GenerationStats] = []
    stagnant_generations = 0

    start_time = time.perf_counter()

    for generation in range(1, config.generations + 1):
        distances, fitnesses = evaluate_population(population, distance_matrix)

        if _should_run_two_opt(
            generation=generation,
            config=config,
            best_distance=best_distance,
            stagnant_generations=stagnant_generations,
        ):
            _improve_elites_with_two_opt(population, distances, fitnesses, distance_matrix, config, instance.dimension)

        generation_best_index = min(range(len(population)), key=lambda idx: distances[idx])
        generation_best_route = population[generation_best_index][:]
        generation_best_distance = distances[generation_best_index]

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

        _print_progress(
            config=config,
            generation=generation,
            best_distance=int(best_distance),
            generation_best_distance=generation_best_distance,
            average_distance=generation_average,
            stagnant_generations=stagnant_generations,
        )

        if stagnant_generations >= config.restart_stagnation:
            population = _restart_population(instance.dimension, distance_matrix, config, rng, best_route)
            stagnant_generations = 0
            continue

        elites = select_elites(population, distances, config.elite_size)
        offspring = _create_offspring(
            population=population,
            fitnesses=fitnesses,
            config=config,
            rng=rng,
            distance_matrix=distance_matrix,
            generation=generation,
        )
        population = next_generation(elites, offspring, config.population_size)

        if stagnant_generations >= config.two_opt_stagnation:
            _inject_random_immigrants(population, instance.dimension, distance_matrix, config, rng)

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
        if config.show_progress:
            seed_index = len(run_results) + 1
            print(f"Running seed {seed_index}/{len(seeds)}: {seed}")
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
    distance_matrix: list[list[int]],
    generation: int,
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
            if rng.random() < config.scx_crossover_rate:
                child1 = sequential_constructive_crossover(parent1, parent2, distance_matrix, rng)
                child2 = sequential_constructive_crossover(parent2, parent1, distance_matrix, rng)
                stage = "scx crossover"
            else:
                start, end = _random_segment(num_cities, rng)
                child1, child2 = order_crossover(parent1, parent2, start, end)
                stage = "crossover"
            if config.validate_permutations:
                _validate_permutation(child1, num_cities, stage)
                _validate_permutation(child2, num_cities, stage)

        if rng.random() < config.mutation_rate:
            child1 = adaptive_mutation(child1, generation, config.generations, rng)
            if config.validate_permutations:
                _validate_permutation(child1, num_cities, "mutation")

        if rng.random() < config.mutation_rate:
            child2 = adaptive_mutation(child2, generation, config.generations, rng)
            if config.validate_permutations:
                _validate_permutation(child2, num_cities, "mutation")

        if config.use_two_opt and rng.random() < config.child_two_opt_rate:
            child1, _ = two_opt_local_search(child1, distance_matrix)
        if config.use_two_opt and rng.random() < config.child_two_opt_rate:
            child2, _ = two_opt_local_search(child2, distance_matrix)

        offspring.append(child1)
        if len(offspring) < target_size:
            offspring.append(child2)

    return offspring


def _print_progress(
    config: GAConfig,
    generation: int,
    best_distance: int,
    generation_best_distance: int,
    average_distance: float,
    stagnant_generations: int,
) -> None:
    if not config.show_progress:
        return
    if generation != 1 and generation != config.generations and generation % config.progress_interval != 0:
        return

    progress = generation / config.generations
    filled = int(config.progress_bar_width * progress)
    bar = "#" * filled + "." * (config.progress_bar_width - filled)
    seed = "none" if config.random_seed is None else str(config.random_seed)
    print(
        f"[seed={seed}] Gen {generation}/{config.generations} [{bar}] "
        f"best={best_distance} gen_best={generation_best_distance} "
        f"avg={average_distance:.2f} stagnant={stagnant_generations}"
    )


def _should_run_two_opt(
    generation: int,
    config: GAConfig,
    best_distance: float,
    stagnant_generations: int,
) -> bool:
    if not config.use_two_opt:
        return False
    if best_distance == float("inf"):
        return True
    if stagnant_generations >= config.two_opt_stagnation:
        return True
    return generation % config.two_opt_interval == 0


def _improve_elites_with_two_opt(
    population: list[list[int]],
    distances: list[int],
    fitnesses: list[float],
    distance_matrix: list[list[int]],
    config: GAConfig,
    num_cities: int,
) -> None:
    elite_count = min(config.local_search_elite_count, len(population))
    ranked_indices = sorted(range(len(population)), key=lambda idx: distances[idx])[:elite_count]

    for index in ranked_indices:
        improved_route, improved_distance = two_opt_local_search(population[index], distance_matrix)
        if config.validate_permutations:
            _validate_permutation(improved_route, num_cities, "2-opt")
        if improved_distance < distances[index]:
            population[index] = improved_route
            distances[index] = improved_distance
            fitnesses[index] = 1.0 / (improved_distance + 1e-12)


def _inject_random_immigrants(
    population: list[list[int]],
    num_cities: int,
    distance_matrix: list[list[int]],
    config: GAConfig,
    rng: random.Random,
) -> None:
    immigrant_count = int(config.population_size * config.immigrant_fraction)
    if immigrant_count <= 0:
        return

    immigrants = initialize_population(
        immigrant_count,
        num_cities,
        rng,
        distance_matrix=distance_matrix,
        greedy_fraction=0.25,
        randomized_greedy_fraction=0.50,
    )
    start = max(config.elite_size, len(population) - immigrant_count)
    population[start:] = immigrants[: len(population) - start]


def _restart_population(
    num_cities: int,
    distance_matrix: list[list[int]],
    config: GAConfig,
    rng: random.Random,
    best_route: list[int],
) -> list[list[int]]:
    population = [best_route[:]] if best_route else []
    population.extend(
        initialize_population(
            config.population_size - len(population),
            num_cities,
            rng,
            distance_matrix=distance_matrix,
            greedy_fraction=config.greedy_initial_fraction,
            randomized_greedy_fraction=config.randomized_greedy_initial_fraction,
        )
    )
    return population[: config.population_size]


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
