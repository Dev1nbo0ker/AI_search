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

    population_size: int = 500
    generations: int = 3000
    crossover_rate: float = 0.9
    mutation_rate: float = 0.2
    elite_size: int = 5
    tournament_size: int = 3
    random_seed: int | None = None
    use_two_opt: bool = True
    two_opt_interval: int = 10
    two_opt_stagnation: int = 40
    local_search_elite_count: int = 4
    child_two_opt_rate: float = 0.03
    greedy_initial_fraction: float = 0.35
    randomized_greedy_initial_fraction: float = 0.35
    immigrant_fraction: float = 0.12
    restart_stagnation: int = 250
    scx_crossover_rate: float = 0.35
    show_progress: bool = True
    progress_interval: int = 50
    progress_bar_width: int = 32
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
