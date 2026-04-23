from __future__ import annotations

import argparse

from tsp_ga.models import GAConfig


DEFAULT_CONFIG = GAConfig(
    population_size=300,
    generations=2000,
    crossover_rate=0.9,
    mutation_rate=0.15,
    elite_size=3,
    tournament_size=3,
    random_seed=42,
    use_two_opt=True,
    two_opt_interval=20,
    two_opt_stagnation=50,
    validate_permutations=False,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Solve a TSPLIB EUC_2D TSP instance using a genetic algorithm.",
    )
    parser.add_argument("file_path", help="Path to a TSPLIB EUC_2D file.")
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42],
        help="Run the solver multiple times with the given random seeds.",
    )
    parser.add_argument(
        "--disable-2opt",
        action="store_true",
        help="Disable the optional 2-opt local search on the best individual of each generation.",
    )
    return parser


def parse_args() -> tuple[str, GAConfig, list[int]]:
    parser = build_parser()
    args = parser.parse_args()
    config = GAConfig(
        population_size=DEFAULT_CONFIG.population_size,
        generations=DEFAULT_CONFIG.generations,
        crossover_rate=DEFAULT_CONFIG.crossover_rate,
        mutation_rate=DEFAULT_CONFIG.mutation_rate,
        elite_size=DEFAULT_CONFIG.elite_size,
        tournament_size=DEFAULT_CONFIG.tournament_size,
        random_seed=DEFAULT_CONFIG.random_seed,
        use_two_opt=not args.disable_2opt,
        two_opt_interval=DEFAULT_CONFIG.two_opt_interval,
        two_opt_stagnation=DEFAULT_CONFIG.two_opt_stagnation,
        validate_permutations=DEFAULT_CONFIG.validate_permutations,
    )
    return args.file_path, config, args.seeds


def validate_config(config: GAConfig, num_cities: int) -> None:
    if config.population_size < 2:
        raise ValueError("population_size must be at least 2.")
    if config.generations < 1:
        raise ValueError("generations must be at least 1.")
    if not 0.0 <= config.crossover_rate <= 1.0:
        raise ValueError("crossover_rate must be in [0, 1].")
    if not 0.0 <= config.mutation_rate <= 1.0:
        raise ValueError("mutation_rate must be in [0, 1].")
    if config.elite_size < 0:
        raise ValueError("elite_size cannot be negative.")
    if config.elite_size >= config.population_size:
        raise ValueError("elite_size must be smaller than population_size.")
    if config.tournament_size < 2:
        raise ValueError("tournament_size must be at least 2.")
    if config.tournament_size > config.population_size:
        raise ValueError("tournament_size cannot exceed population_size.")
    if config.two_opt_interval < 1:
        raise ValueError("two_opt_interval must be at least 1.")
    if config.two_opt_stagnation < 1:
        raise ValueError("two_opt_stagnation must be at least 1.")
    if num_cities < 2:
        raise ValueError("TSP instance must contain at least 2 cities.")
