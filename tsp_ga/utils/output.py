from __future__ import annotations

from tsp_ga.models import ExperimentResult, GAResult, GenerationStats, TSPInstance

LOG_INTERVAL = 50


def print_summary(instance: TSPInstance, result: GAResult) -> None:
    route_text = " -> ".join(str(city) for city in result.best_route)
    print(f"Instance: {instance.name}")
    print(f"Seed: {result.seed}")
    print(f"Best route: {route_text}")
    print(f"Best distance: {result.best_distance}")
    print(f"Best value every {LOG_INTERVAL} generations:")
    for generation, best_value in _iter_generation_best(result.generation_best, LOG_INTERVAL):
        print(f"  Generation {generation}: {best_value}")
    print(f"Runtime: {result.runtime_seconds:.6f} seconds")


def print_experiment_summary(instance: TSPInstance, experiment: ExperimentResult) -> None:
    print(f"Instance: {instance.name}")
    print("Run summary:")
    for run in experiment.runs:
        print(
            f"  Seed {run.seed}: "
            f"best distance = {run.best_distance}, "
            f"runtime = {run.runtime_seconds:.6f} seconds"
        )
    print(f"Best distance: {experiment.best_run.best_distance}")
    print(f"Mean distance: {experiment.mean_distance:.2f}")
    print(f"Worst distance: {experiment.worst_distance}")
    print(f"Best seed: {experiment.best_run.seed}")
    route_text = " -> ".join(str(city) for city in experiment.best_run.best_route)
    print(f"Best route: {route_text}")
    print(f"Total runtime: {experiment.total_runtime_seconds:.6f} seconds")
    print(f"Best value every {LOG_INTERVAL} generations (best run):")
    for generation, best_value in _iter_generation_best(experiment.best_run.generation_best, LOG_INTERVAL):
        print(f"  Generation {generation}: {best_value}")


def print_generation_table(history: list[GenerationStats]) -> None:
    print(f"\nGeneration statistics (every {LOG_INTERVAL} generations):")
    for item in _iter_history(history, LOG_INTERVAL):
        print(
            f"  Gen {item.generation:4d} | "
            f"Best distance = {item.best_distance:6d} | "
            f"Average distance = {item.average_distance:10.2f}"
        )


def _iter_generation_best(values: list[int], interval: int) -> list[tuple[int, int]]:
    sampled = [(index, values[index - 1]) for index in range(interval, len(values) + 1, interval)]
    if not sampled or sampled[-1][0] != len(values):
        sampled.append((len(values), values[-1]))
    return sampled


def _iter_history(history: list[GenerationStats], interval: int) -> list[GenerationStats]:
    sampled = [item for item in history if item.generation % interval == 0]
    if not sampled or sampled[-1].generation != history[-1].generation:
        sampled.append(history[-1])
    return sampled
