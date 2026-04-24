from __future__ import annotations

import argparse

from tsp_ga.models import GAConfig


DEFAULT_CONFIG = GAConfig(
    population_size=500,
    generations=3000,
    crossover_rate=0.9,
    mutation_rate=0.2,
    elite_size=5,
    tournament_size=3,
    random_seed=42,
    use_two_opt=True,
    two_opt_interval=10,
    two_opt_stagnation=40,
    local_search_elite_count=4,
    child_two_opt_rate=0.03,
    greedy_initial_fraction=0.35,
    randomized_greedy_initial_fraction=0.35,
    immigrant_fraction=0.12,
    restart_stagnation=250,
    scx_crossover_rate=0.35,
    show_progress=True,
    progress_interval=50,
    progress_bar_width=32,
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
        help="Disable local 2-opt polishing.",
    )
    parser.add_argument("--population-size", type=int, default=DEFAULT_CONFIG.population_size)
    parser.add_argument("--generations", type=int, default=DEFAULT_CONFIG.generations)
    parser.add_argument("--mutation-rate", type=float, default=DEFAULT_CONFIG.mutation_rate)
    parser.add_argument("--crossover-rate", type=float, default=DEFAULT_CONFIG.crossover_rate)
    parser.add_argument("--elite-size", type=int, default=DEFAULT_CONFIG.elite_size)
    parser.add_argument("--tournament-size", type=int, default=DEFAULT_CONFIG.tournament_size)
    parser.add_argument("--local-search-elites", type=int, default=DEFAULT_CONFIG.local_search_elite_count)
    parser.add_argument("--child-2opt-rate", type=float, default=DEFAULT_CONFIG.child_two_opt_rate)
    parser.add_argument("--two-opt-interval", type=int, default=DEFAULT_CONFIG.two_opt_interval)
    parser.add_argument("--two-opt-stagnation", type=int, default=DEFAULT_CONFIG.two_opt_stagnation)
    parser.add_argument("--greedy-fraction", type=float, default=DEFAULT_CONFIG.greedy_initial_fraction)
    parser.add_argument(
        "--randomized-greedy-fraction",
        type=float,
        default=DEFAULT_CONFIG.randomized_greedy_initial_fraction,
    )
    parser.add_argument("--immigrant-fraction", type=float, default=DEFAULT_CONFIG.immigrant_fraction)
    parser.add_argument("--restart-stagnation", type=int, default=DEFAULT_CONFIG.restart_stagnation)
    parser.add_argument("--scx-rate", type=float, default=DEFAULT_CONFIG.scx_crossover_rate)
    parser.add_argument("--no-progress", action="store_true", help="Disable generation progress output.")
    parser.add_argument("--progress-interval", type=int, default=DEFAULT_CONFIG.progress_interval)
    return parser


def parse_args() -> tuple[str, GAConfig, list[int]]:
    parser = build_parser()
    args = parser.parse_args()
    config = GAConfig(
        population_size=args.population_size,
        generations=args.generations,
        crossover_rate=args.crossover_rate,
        mutation_rate=args.mutation_rate,
        elite_size=args.elite_size,
        tournament_size=args.tournament_size,
        random_seed=DEFAULT_CONFIG.random_seed,
        use_two_opt=not args.disable_2opt,
        two_opt_interval=args.two_opt_interval,
        two_opt_stagnation=args.two_opt_stagnation,
        local_search_elite_count=args.local_search_elites,
        child_two_opt_rate=args.child_2opt_rate,
        greedy_initial_fraction=args.greedy_fraction,
        randomized_greedy_initial_fraction=args.randomized_greedy_fraction,
        immigrant_fraction=args.immigrant_fraction,
        restart_stagnation=args.restart_stagnation,
        scx_crossover_rate=args.scx_rate,
        show_progress=not args.no_progress,
        progress_interval=args.progress_interval,
        progress_bar_width=DEFAULT_CONFIG.progress_bar_width,
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
    if config.local_search_elite_count < 1:
        raise ValueError("local_search_elite_count must be at least 1.")
    if not 0.0 <= config.child_two_opt_rate <= 1.0:
        raise ValueError("child_two_opt_rate must be in [0, 1].")
    if not 0.0 <= config.greedy_initial_fraction <= 1.0:
        raise ValueError("greedy_initial_fraction must be in [0, 1].")
    if not 0.0 <= config.randomized_greedy_initial_fraction <= 1.0:
        raise ValueError("randomized_greedy_initial_fraction must be in [0, 1].")
    if config.greedy_initial_fraction + config.randomized_greedy_initial_fraction > 1.0:
        raise ValueError("initialization fractions cannot sum to more than 1.")
    if not 0.0 <= config.immigrant_fraction <= 1.0:
        raise ValueError("immigrant_fraction must be in [0, 1].")
    if config.restart_stagnation < 1:
        raise ValueError("restart_stagnation must be at least 1.")
    if not 0.0 <= config.scx_crossover_rate <= 1.0:
        raise ValueError("scx_crossover_rate must be in [0, 1].")
    if config.progress_interval < 1:
        raise ValueError("progress_interval must be at least 1.")
    if config.progress_bar_width < 1:
        raise ValueError("progress_bar_width must be at least 1.")
    if num_cities < 2:
        raise ValueError("TSP instance must contain at least 2 cities.")
