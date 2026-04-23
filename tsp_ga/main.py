from __future__ import annotations

from tsp_ga.config import parse_args
from tsp_ga.ga.solver import run_multiple_seeds
from tsp_ga.io.tsplib_parser import load_tsplib_euc2d
from tsp_ga.utils.output import print_experiment_summary, print_generation_table


def main() -> None:
    file_path, config, seeds = parse_args()
    instance = load_tsplib_euc2d(file_path)
    result, history = run_multiple_seeds(instance, config, seeds)
    print_experiment_summary(instance, result)
    print_generation_table(history)


if __name__ == "__main__":
    main()
