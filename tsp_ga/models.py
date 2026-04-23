from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TSPInstance:
    """Parsed TSPLIB instance data."""

    name: str
    dimension: int
    node_ids: list[int]
    coordinates: list[tuple[float, float]]


@dataclass(frozen=True)
class GAConfig:
    """Configurable parameters for the genetic algorithm."""

    population_size: int = 300
    generations: int = 2000
    crossover_rate: float = 0.9
    mutation_rate: float = 0.15
    elite_size: int = 3
    tournament_size: int = 3
    random_seed: int | None = None
    use_two_opt: bool = True
    two_opt_interval: int = 20
    two_opt_stagnation: int = 50
    validate_permutations: bool = False


@dataclass
class GenerationStats:
    """Summary statistics for one generation."""

    generation: int
    best_distance: int
    average_distance: float


@dataclass
class GAResult:
    """Final optimization output."""

    seed: int | None
    best_route: list[int]
    best_distance: int
    generation_best: list[int]
    runtime_seconds: float


@dataclass
class ExperimentResult:
    """Summary of multiple runs under different random seeds."""

    runs: list[GAResult]
    best_run: GAResult
    mean_distance: float
    worst_distance: int
    total_runtime_seconds: float
