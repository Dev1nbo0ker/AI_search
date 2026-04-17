from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Callable, Optional

State = tuple[int, ...]
Move = str
HeuristicFunc = Callable[[State], int]

N = 4
SIZE = N * N
GOAL_STATE: State = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

GOAL_POS: dict[int, tuple[int, int]] = {
    tile: divmod(idx, N) for idx, tile in enumerate(GOAL_STATE) if tile != 0
}

REVERSE_MOVE: dict[Move, Move] = {"U": "D", "D": "U", "L": "R", "R": "L"}

# 5-5-5 disjoint patterns for additive PDB.
# Each group contains disjoint tiles, while blank is shared abstractly.
PDB_PATTERNS: tuple[tuple[int, ...], ...] = (
    (1, 2, 3, 4, 5),
    (6, 7, 8, 9, 10),
    (11, 12, 13, 14, 15),
)

# Adjacency of blank moves for each index in the 4x4 board.
BLANK_ADJ: tuple[tuple[int, ...], ...] = tuple(
    tuple(
        nxt
        for nxt in (
            idx - N if idx // N > 0 else -1,
            idx + N if idx // N < N - 1 else -1,
            idx - 1 if idx % N > 0 else -1,
            idx + 1 if idx % N < N - 1 else -1,
        )
        if nxt != -1
    )
    for idx in range(SIZE)
)

# Lazy-loaded PDB cache:
#   pattern -> distance table (bytearray)
# The table index is the compressed abstract pattern state.
_PDB_TABLES: dict[tuple[int, ...], bytearray] = {}
_PDB_INF = 255


@dataclass
class SearchResult:
    algorithm: str
    heuristic_name: str
    solvable: bool
    solution_length: int
    moves: list[Move]
    expanded_nodes: int
    running_time: float


def validate_state(state: State) -> None:
    """Validate that a state is a permutation of 0..15 with length 16."""
    if len(state) != SIZE:
        raise ValueError(f"state length must be {SIZE}, got {len(state)}")
    if set(state) != set(range(SIZE)):
        raise ValueError("state must contain each number 0..15 exactly once")


def is_goal(state: State) -> bool:
    return state == GOAL_STATE


def inversion_count(state: State) -> int:
    """Count inversions, ignoring 0."""
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        ai = arr[i]
        for j in range(i + 1, len(arr)):
            if ai > arr[j]:
                inv += 1
    return inv


def is_solvable(state: State) -> bool:
    """
    Solvability test for 4x4 puzzle.
    For even grid width:
      - blank on odd row from bottom => inversions must be even
      - blank on even row from bottom => inversions must be odd
    """
    validate_state(state)
    inv = inversion_count(state)
    blank_idx = state.index(0)
    blank_row_from_top = blank_idx // N
    blank_row_from_bottom = N - blank_row_from_top
    if blank_row_from_bottom % 2 == 1:
        return inv % 2 == 0
    return inv % 2 == 1


def get_neighbors(state: State) -> list[tuple[Move, State]]:
    """Generate neighbor states in U, D, L, R order."""
    blank = state.index(0)
    r, c = divmod(blank, N)
    neighbors: list[tuple[Move, State]] = []

    def swapped(new_blank: int) -> State:
        arr = list(state)
        arr[blank], arr[new_blank] = arr[new_blank], arr[blank]
        return tuple(arr)

    if r > 0:
        neighbors.append(("U", swapped(blank - N)))
    if r < N - 1:
        neighbors.append(("D", swapped(blank + N)))
    if c > 0:
        neighbors.append(("L", swapped(blank - 1)))
    if c < N - 1:
        neighbors.append(("R", swapped(blank + 1)))
    return neighbors


def manhattan_distance(state: State) -> int:
    """Sum of Manhattan distances for all numbered tiles."""
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(idx, N)
        gr, gc = GOAL_POS[tile]
        dist += abs(r - gr) + abs(c - gc)
    return dist


def linear_conflict(state: State) -> int:
    """
    Linear conflict cost (extra over Manhattan).
    Each conflicting pair contributes +2.
    """
    conflict = 0

    # Row conflicts.
    for row in range(N):
        row_tiles: list[int] = []
        for col in range(N):
            tile = state[row * N + col]
            if tile == 0:
                continue
            goal_row, _ = GOAL_POS[tile]
            if goal_row == row:
                row_tiles.append(tile)
        for i in range(len(row_tiles)):
            _, goal_col_i = GOAL_POS[row_tiles[i]]
            for j in range(i + 1, len(row_tiles)):
                _, goal_col_j = GOAL_POS[row_tiles[j]]
                if goal_col_i > goal_col_j:
                    conflict += 2

    # Column conflicts.
    for col in range(N):
        col_tiles: list[int] = []
        for row in range(N):
            tile = state[row * N + col]
            if tile == 0:
                continue
            _, goal_col = GOAL_POS[tile]
            if goal_col == col:
                col_tiles.append(tile)
        for i in range(len(col_tiles)):
            goal_row_i, _ = GOAL_POS[col_tiles[i]]
            for j in range(i + 1, len(col_tiles)):
                goal_row_j, _ = GOAL_POS[col_tiles[j]]
                if goal_row_i > goal_row_j:
                    conflict += 2

    return conflict


def heuristic_manhattan(state: State) -> int:
    return manhattan_distance(state)


def heuristic_manhattan_linear_conflict(state: State) -> int:
    return manhattan_distance(state) + linear_conflict(state)


def _encode_pattern_state(blank_pos: int, tile_positions: tuple[int, ...]) -> int:
    """
    Compress abstract pattern state into an int using 4-bit slots:
      bits [0:4): blank position
      bits [4:8): tile_positions[0]
      bits [8:12): tile_positions[1]
      ...
    """
    enc = blank_pos
    shift = 4
    for pos in tile_positions:
        enc |= pos << shift
        shift += 4
    return enc


def _encode_pattern_from_full_state(state: State, pattern: tuple[int, ...]) -> int:
    """Encode one pattern abstraction from a full board state."""
    tile_to_pos = [0] * SIZE
    for idx, tile in enumerate(state):
        tile_to_pos[tile] = idx
    blank_pos = tile_to_pos[0]
    tile_positions = tuple(tile_to_pos[tile] for tile in pattern)
    return _encode_pattern_state(blank_pos, tile_positions)


def _build_single_pdb(pattern: tuple[int, ...]) -> bytearray:
    """
    Build one pattern database with reverse 0-1 BFS from goal abstraction.
    Transition cost:
      - 1 if moved tile belongs to this pattern
      - 0 otherwise
    This cost partitioning is what makes additive sum admissible.
    """
    k = len(pattern)
    table_size = 1 << (4 * (k + 1))
    dist = bytearray([_PDB_INF]) * table_size

    goal_enc = _encode_pattern_from_full_state(GOAL_STATE, pattern)
    dist[goal_enc] = 0
    dq: deque[int] = deque([goal_enc])

    while dq:
        enc = dq.popleft()
        cur_d = dist[enc]
        blank = enc & 0xF

        for nb in BLANK_ADJ[blank]:
            # Check whether a pattern tile occupies position nb in this abstract state.
            moved_shift = -1
            for i in range(k):
                shift = 4 * (i + 1)
                if ((enc >> shift) & 0xF) == nb:
                    moved_shift = shift
                    break

            # Always move blank to nb.
            new_enc = (enc & ~0xF) | nb

            if moved_shift == -1:
                # Blank swaps with a non-pattern tile (cost 0 for this pattern).
                weight = 0
            else:
                # Blank swaps with a pattern tile (cost 1 for this pattern).
                mask = 0xF << moved_shift
                new_enc = (new_enc & ~mask) | (blank << moved_shift)
                weight = 1

            nd = cur_d + weight
            if nd < dist[new_enc]:
                dist[new_enc] = nd
                if weight == 0:
                    dq.appendleft(new_enc)
                else:
                    dq.append(new_enc)

    return dist


def _ensure_pdb_built() -> None:
    """Lazily build all pattern databases once."""
    if _PDB_TABLES:
        return
    for pattern in PDB_PATTERNS:
        _PDB_TABLES[pattern] = _build_single_pdb(pattern)


def heuristic_pdb(state: State) -> int:
    """
    Additive disjoint PDB heuristic (5-5-5 split).
    Admissible because each move cost is charged to exactly one tile group.
    """
    _ensure_pdb_built()
    h = 0
    for pattern in PDB_PATTERNS:
        enc = _encode_pattern_from_full_state(state, pattern)
        d = _PDB_TABLES[pattern][enc]
        if d == _PDB_INF:
            # Should not happen for valid states; safe fallback.
            return manhattan_distance(state)
        h += d
    return h


def reconstruct_path(
    parent: dict[State, Optional[tuple[State, Move]]], end_state: State
) -> list[Move]:
    moves: list[Move] = []
    cur = end_state
    while True:
        entry = parent[cur]
        if entry is None:
            break
        prev, move = entry
        moves.append(move)
        cur = prev
    moves.reverse()
    return moves


def astar(start: State, heuristic: HeuristicFunc) -> SearchResult:
    validate_state(start)
    t0 = perf_counter()
    h_name = getattr(heuristic, "__name__", "heuristic")

    if not is_solvable(start):
        return SearchResult(
            algorithm="A*",
            heuristic_name=h_name,
            solvable=False,
            solution_length=0,
            moves=[],
            expanded_nodes=0,
            running_time=perf_counter() - t0,
        )

    open_heap: list[tuple[int, int, int, State]] = []
    g_score: dict[State, int] = {start: 0}
    parent: dict[State, Optional[tuple[State, Move]]] = {start: None}
    expanded_nodes = 0
    tie = count()

    h0 = heuristic(start)
    heappush(open_heap, (h0, 0, next(tie), start))

    while open_heap:
        f_cur, g_cur, _, state = heappop(open_heap)
        best_g = g_score.get(state)
        if best_g is None or g_cur != best_g:
            continue

        if is_goal(state):
            path = reconstruct_path(parent, state)
            return SearchResult(
                algorithm="A*",
                heuristic_name=h_name,
                solvable=True,
                solution_length=len(path),
                moves=path,
                expanded_nodes=expanded_nodes,
                running_time=perf_counter() - t0,
            )

        expanded_nodes += 1
        for move, nxt in get_neighbors(state):
            ng = g_cur + 1
            old = g_score.get(nxt)
            if old is None or ng < old:
                g_score[nxt] = ng
                parent[nxt] = (state, move)
                nf = ng + heuristic(nxt)
                heappush(open_heap, (nf, ng, next(tie), nxt))

    return SearchResult(
        algorithm="A*",
        heuristic_name=h_name,
        solvable=False,
        solution_length=0,
        moves=[],
        expanded_nodes=expanded_nodes,
        running_time=perf_counter() - t0,
    )


def idastar(start: State, heuristic: HeuristicFunc) -> SearchResult:
    validate_state(start)
    t0 = perf_counter()
    h_name = getattr(heuristic, "__name__", "heuristic")

    if not is_solvable(start):
        return SearchResult(
            algorithm="IDA*",
            heuristic_name=h_name,
            solvable=False,
            solution_length=0,
            moves=[],
            expanded_nodes=0,
            running_time=perf_counter() - t0,
        )

    FOUND = object()
    expanded_nodes = 0
    bound = heuristic(start)
    path_moves: list[Move] = []
    path_states: set[State] = {start}

    def dfs(state: State, g: int, threshold: int, prev_move: Optional[Move]) -> object:
        nonlocal expanded_nodes
        h = heuristic(state)
        f = g + h
        if f > threshold:
            return f
        if is_goal(state):
            return FOUND

        expanded_nodes += 1
        min_exceed = float("inf")

        for move, nxt in get_neighbors(state):
            # Avoid immediate backtracking and repeated states on current path.
            if prev_move is not None and move == REVERSE_MOVE[prev_move]:
                continue
            if nxt in path_states:
                continue

            path_states.add(nxt)
            path_moves.append(move)

            res = dfs(nxt, g + 1, threshold, move)
            if res is FOUND:
                return FOUND
            if isinstance(res, (int, float)) and res < min_exceed:
                min_exceed = res

            path_moves.pop()
            path_states.remove(nxt)

        return min_exceed

    while True:
        res = dfs(start, 0, bound, None)
        if res is FOUND:
            return SearchResult(
                algorithm="IDA*",
                heuristic_name=h_name,
                solvable=True,
                solution_length=len(path_moves),
                moves=path_moves.copy(),
                expanded_nodes=expanded_nodes,
                running_time=perf_counter() - t0,
            )
        if not isinstance(res, (int, float)) or res == float("inf"):
            return SearchResult(
                algorithm="IDA*",
                heuristic_name=h_name,
                solvable=False,
                solution_length=0,
                moves=[],
                expanded_nodes=expanded_nodes,
                running_time=perf_counter() - t0,
            )
        # res must be strictly greater than current bound when not found.
        bound = int(res)


def apply_moves(state: State, moves: list[Move]) -> State:
    """Apply a move sequence to construct test states."""
    cur = state
    for mv in moves:
        next_state: Optional[State] = None
        for move, nxt in get_neighbors(cur):
            if move == mv:
                next_state = nxt
                break
        if next_state is None:
            raise ValueError(f"invalid move {mv} for state {cur}")
        cur = next_state
    return cur


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
    """
    Benchmark all (algorithm x heuristic) combinations for each test case.
    Prints one table per case.
    """
    algorithms: list[tuple[str, Callable[[State, HeuristicFunc], SearchResult]]] = [
        ("A*", astar),
        ("IDA*", idastar),
    ]
    heuristics: list[tuple[str, HeuristicFunc]] = [
        ("Manhattan Distance", heuristic_manhattan),
        ("Manhattan + Linear Conflict", heuristic_manhattan_linear_conflict),
        ("Disjoint Additive PDB", heuristic_pdb),
    ]

    # Precompute PDB once, and report its preprocessing time separately.
    t0 = perf_counter()
    _ensure_pdb_built()
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
    print("Summary")
    print("1) 最容易实现: Manhattan Distance（代码最短、调试成本最低）")
    print("2) 最强启发式: Disjoint Additive PDB（通常扩展节点最少）")
    print("3) 最适合课程展示: Manhattan + Linear Conflict")
    print("   理由: 在实现复杂度与效果提升之间平衡最好，便于课堂讲解和实验对比。")


def run_case(case_name: str, state: State) -> None:
    print("=" * 72)
    print(f"Case: {case_name}")
    print(f"State: {state}")
    print(f"Solvable check: {is_solvable(state)}")

    algorithms = [astar, idastar]
    heuristics: list[HeuristicFunc] = [
        heuristic_manhattan,
        heuristic_manhattan_linear_conflict,
        heuristic_pdb,
    ]

    for algo in algorithms:
        for heu in heuristics:
            result = algo(state, heu)
            print("-" * 72)
            print(format_result(result))


def main() -> None:
    # 1) Already goal state.
    case_goal = GOAL_STATE

    # 2) One move away from goal.
    case_one_move = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)

    # 3) A medium solvable state created by valid scramble moves.
    scramble = ["L", "U", "L", "U", "R", "D", "L", "D", "R", "U", "R", "D"]
    case_medium = apply_moves(GOAL_STATE, scramble)

    cases = [
        ("Already Goal", case_goal),
        ("One Move Away", case_one_move),
        ("Medium Solvable", case_medium),
    ]
    run_benchmark_experiment(cases)


if __name__ == "__main__":
    main()
