from __future__ import annotations

from time import perf_counter

from .heuristics import (
    ensure_pdb_built,
    heuristic_manhattan,
    heuristic_manhattan_linear_conflict,
    heuristic_pdb,
)
from .search import astar, idastar
from .types import HeuristicFunc, SearchResult, State


def format_result(result: SearchResult) -> str:
    seq = "".join(result.moves) if result.moves else "(empty)"
    lines = [
        f"Algorithm      : {result.algorithm}",
        f"Heuristic      : {result.heuristic_name}",
        f"Solvable       : {result.solvable}",
        f"Solution length: {result.solution_length}",
        f"Moves          : {seq}",
        f"Expanded nodes : {result.expanded_nodes}",
        f"Running time   : {result.running_time:.6f} s",
    ]
    return "\n".join(lines)


def format_benchmark_table(rows: list[tuple[str, str, str, str, str, str]]) -> str:
    headers = (
        "algorithm",
        "heuristic",
        "solvable",
        "solution length",
        "expanded nodes",
        "running time (s)",
    )
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    def fmt_row(values: tuple[str, ...]) -> str:
        return " | ".join(values[i].ljust(widths[i]) for i in range(len(values)))

    sep = "-+-".join("-" * w for w in widths)
    lines = [fmt_row(headers), sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def run_benchmark_experiment(cases: list[tuple[str, State]]) -> None:
    algorithms = [("A*", astar), ("IDA*", idastar)]
    heuristics: list[tuple[str, HeuristicFunc]] = [
        ("Manhattan Distance", heuristic_manhattan),
        ("Manhattan + Linear Conflict", heuristic_manhattan_linear_conflict),
        ("Disjoint Additive PDB", heuristic_pdb),
    ]

    t0 = perf_counter()
    ensure_pdb_built()
    pdb_build_time = perf_counter() - t0

    print("=" * 72)
    print("Benchmark / Experiment")
    print(f"PDB preprocessing time (one-time): {pdb_build_time:.6f} s")

    for case_name, state in cases:
        print("=" * 72)
        print(f"Case: {case_name}")
        print(f"State: {state}")

        rows: list[tuple[str, str, str, str, str, str]] = []
        for algo_name, algo_fn in algorithms:
            for heu_name, heu_fn in heuristics:
                result = algo_fn(state, heu_fn)
                rows.append(
                    (
                        algo_name,
                        heu_name,
                        str(result.solvable),
                        str(result.solution_length),
                        str(result.expanded_nodes),
                        f"{result.running_time:.6f}",
                    )
                )
        print(format_benchmark_table(rows))

    print("=" * 72)
    

