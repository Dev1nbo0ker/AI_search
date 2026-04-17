from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

Pos = tuple[int, int]


@dataclass
class MazeProblem:
    # 迷宫问题定义：网格 + 起终点 + 尺寸
    grid: list[list[str]]
    start: Pos
    end: Pos
    rows: int
    cols: int


@dataclass
class SearchResult:
    # 统一结果结构，便于不同算法横向比较
    algorithm: str
    found: bool
    path: list[Pos]
    visited_count: int
    status: Literal["success", "failure", "cutoff"]
    depth: int


def parse_maze(lines: list[str]) -> MazeProblem:
    # 读取并校验迷宫（矩形、字符合法、S/E 唯一）
    cleaned: list[list[str]] = []
    allowed = {"S", "E", "0", "1"}

    for raw in lines:
        row = [ch for ch in raw.strip().replace(" ", "")]
        if row:
            cleaned.append(row)

    if not cleaned:
        raise ValueError("Maze cannot be empty.")

    cols = len(cleaned[0])
    for row in cleaned:
        if len(row) != cols:
            raise ValueError("Maze must be rectangular.")
        for ch in row:
            if ch not in allowed:
                raise ValueError(f"Invalid maze character: {ch}")

    start_positions: list[Pos] = []
    end_positions: list[Pos] = []
    for r, row in enumerate(cleaned):
        for c, ch in enumerate(row):
            if ch == "S":
                start_positions.append((r, c))
            elif ch == "E":
                end_positions.append((r, c))

    if len(start_positions) != 1 or len(end_positions) != 1:
        raise ValueError("Maze must contain exactly one S and one E.")

    return MazeProblem(
        grid=cleaned,
        start=start_positions[0],
        end=end_positions[0],
        rows=len(cleaned),
        cols=cols,
    )


def in_bounds(problem: MazeProblem, pos: Pos) -> bool:
    r, c = pos
    return 0 <= r < problem.rows and 0 <= c < problem.cols


def is_passable(problem: MazeProblem, pos: Pos) -> bool:
    r, c = pos
    return problem.grid[r][c] != "1"


def neighbors(problem: MazeProblem, pos: Pos) -> list[Pos]:
    r, c = pos
    # 固定扩展顺序：上右下左，保证结果可复现
    order = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # up, right, down, left
    result: list[Pos] = []
    for dr, dc in order:
        nxt = (r + dr, c + dc)
        if in_bounds(problem, nxt) and is_passable(problem, nxt):
            result.append(nxt)
    return result


def reconstruct_path(parent: dict[Pos, Pos | None], end: Pos) -> list[Pos]:
    # 根据父节点字典从终点回溯到起点
    if end not in parent:
        return []
    path: list[Pos] = []
    cur: Pos | None = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def render_path(problem: MazeProblem, path: list[Pos]) -> str:
    # 将最终路径渲染为 *，保留 S/E 不覆盖
    display = [row[:] for row in problem.grid]
    for r, c in path:
        if display[r][c] not in {"S", "E"}:
            display[r][c] = "*"
    return "\n".join("".join(row) for row in display)


def dfs(problem: MazeProblem) -> SearchResult:
    # 深度优先：栈后进先出，优先沿一条路走到底
    stack: list[Pos] = [problem.start]
    parent: dict[Pos, Pos | None] = {problem.start: None}
    visited: set[Pos] = set()
    visited_count = 0

    while stack:
        node = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        visited_count += 1

        if node == problem.end:
            path = reconstruct_path(parent, node)
            return SearchResult("DFS", True, path, visited_count, "success", len(path) - 1)

        # 反向入栈，弹出时仍保持“上右下左”
        for nxt in reversed(neighbors(problem, node)):
            if nxt not in visited and nxt not in parent:
                parent[nxt] = node
                stack.append(nxt)

    return SearchResult("DFS", False, [], visited_count, "failure", -1)


def bfs(problem: MazeProblem) -> SearchResult:
    # 广度优先：队列先进先出，首次到达终点即最短步数路径
    queue: deque[Pos] = deque([problem.start])
    visited: set[Pos] = {problem.start}
    parent: dict[Pos, Pos | None] = {problem.start: None}
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1

        if node == problem.end:
            path = reconstruct_path(parent, node)
            return SearchResult("BFS", True, path, visited_count, "success", len(path) - 1)

        for nxt in neighbors(problem, node):
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = node
                queue.append(nxt)

    return SearchResult("BFS", False, [], visited_count, "failure", -1)


def depth_limited_search(problem: MazeProblem, limit: int) -> SearchResult:
    # 深度受限搜索：超出限制返回 cutoff，不等价于 failure
    if limit < 0:
        raise ValueError("Depth limit must be >= 0.")

    expanded_nodes: set[Pos] = set()

    def recurse(node: Pos, depth: int, path: list[Pos], path_set: set[Pos]) -> tuple[str, list[Pos]]:
        # path_set 仅用于当前递归路径上的去环（避免回到祖先节点）
        expanded_nodes.add(node)
        if node == problem.end:
            return "success", path.copy()
        if depth == limit:
            return "cutoff", []

        cutoff_occurred = False
        for nxt in neighbors(problem, node):
            if nxt in path_set:
                continue
            path.append(nxt)
            path_set.add(nxt)
            status, result_path = recurse(nxt, depth + 1, path, path_set)
            if status == "success":
                return status, result_path
            if status == "cutoff":
                cutoff_occurred = True
            path.pop()
            path_set.remove(nxt)

        if cutoff_occurred:
            return "cutoff", []
        return "failure", []

    status, path = recurse(problem.start, 0, [problem.start], {problem.start})
    found = status == "success"
    depth = len(path) - 1 if found else -1
    return SearchResult("DLS", found, path if found else [], len(expanded_nodes), status, depth)


def iterative_deepening_search(problem: MazeProblem, max_depth: int | None = None) -> SearchResult:
    # 迭代加深：从深度 0 开始逐层增大 limit，结合 DFS 低内存与 BFS 完备性
    if max_depth is None:
        max_depth = problem.rows * problem.cols
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0.")

    total_visited = 0
    last_status: Literal["success", "failure", "cutoff"] = "failure"

    for limit in range(max_depth + 1):
        result = depth_limited_search(problem, limit)
        # 统计每轮 DLS 的访问总量，用于展示 IDS 代价
        total_visited += result.visited_count
        last_status = result.status
        if result.found:
            return SearchResult("IDS", True, result.path, total_visited, "success", result.depth)
        if result.status == "failure":
            return SearchResult("IDS", False, [], total_visited, "failure", -1)

    return SearchResult("IDS", False, [], total_visited, last_status, -1)


def _expand_one_layer(
    problem: MazeProblem,
    frontier: deque[Pos],
    visited_this: set[Pos],
    visited_other: set[Pos],
    parent_this: dict[Pos, Pos | None],
) -> tuple[Pos | None, int]:
    # 双向搜索单侧扩展一步；若新节点被对侧访问过，则找到相遇点
    if not frontier:
        return None, 0

    node = frontier.popleft()
    expanded_count = 1
    for nxt in neighbors(problem, node):
        if nxt in visited_this:
            continue
        visited_this.add(nxt)
        parent_this[nxt] = node
        if nxt in visited_other:
            return nxt, expanded_count
        frontier.append(nxt)
    return None, expanded_count


def _merge_bidirectional_path(
    parent_fwd: dict[Pos, Pos | None],
    parent_bwd: dict[Pos, Pos | None],
    meet: Pos,
) -> list[Pos]:
    # 拼接 S->meet 与 meet->E 两段路径（去重 meet）
    start_to_meet = reconstruct_path(parent_fwd, meet)  # S -> meet
    end_to_meet = reconstruct_path(parent_bwd, meet)  # E -> meet
    meet_to_end = list(reversed(end_to_meet))  # meet -> E
    return start_to_meet + meet_to_end[1:]


def bidirectional_search(problem: MazeProblem) -> SearchResult:
    # 双向搜索：从 S 和 E 同时做 BFS，谁的边界小就先扩展谁
    if problem.start == problem.end:
        return SearchResult("Bidirectional", True, [problem.start], 1, "success", 0)

    frontier_fwd: deque[Pos] = deque([problem.start])
    frontier_bwd: deque[Pos] = deque([problem.end])
    visited_fwd: set[Pos] = {problem.start}
    visited_bwd: set[Pos] = {problem.end}
    parent_fwd: dict[Pos, Pos | None] = {problem.start: None}
    parent_bwd: dict[Pos, Pos | None] = {problem.end: None}
    visited_count = 0

    while frontier_fwd and frontier_bwd:
        if len(frontier_fwd) <= len(frontier_bwd):
            meet, expanded = _expand_one_layer(
                problem, frontier_fwd, visited_fwd, visited_bwd, parent_fwd
            )
        else:
            meet, expanded = _expand_one_layer(
                problem, frontier_bwd, visited_bwd, visited_fwd, parent_bwd
            )

        visited_count += expanded
        if meet is not None:
            path = _merge_bidirectional_path(parent_fwd, parent_bwd, meet)
            return SearchResult(
                "Bidirectional", True, path, visited_count, "success", len(path) - 1
            )

    return SearchResult("Bidirectional", False, [], visited_count, "failure", -1)


def print_result(problem: MazeProblem, result: SearchResult) -> None:
    # 统一打印格式：状态、访问节点数、路径与可视化
    print(f"[{result.algorithm}]")
    print(f"status: {result.status}")
    print(f"visited nodes: {result.visited_count}")
    if result.found:
        print(f"path length: {result.depth}")
        print(f"path: {result.path}")
        print(render_path(problem, result.path))
    else:
        print("No path found.")
        print(render_path(problem, []))
    print("-" * 40)


def run_all(problem: MazeProblem, dls_limit: int, ids_max_depth: int | None = None) -> None:
    # 一次性运行五种算法，便于直接比较结果
    results = [
        dfs(problem),
        bfs(problem),
        depth_limited_search(problem, dls_limit),
        iterative_deepening_search(problem, ids_max_depth),
        bidirectional_search(problem),
    ]

    print(f"DLS limit = {dls_limit}")
    if ids_max_depth is not None:
        print(f"IDS max_depth = {ids_max_depth}")
    print("=" * 40)
    for result in results:
        print_result(problem, result)


def main() -> None:
    maze_lines = [
    "111111111111111111111111111111111111",
    "1000000000000000000000000000000000S1",
    "101111111111111111111111101111111101",
    "101100010001000000111111100011000001",
    "101101010101011110111111111011011111",
    "101101010101000000000000011011000001",
    "101101010101010111100111000011111101",
    "101001010100010000110111111110000001",
    "101101010111111110110000000011011111",
    "101101000110000000111111111011000001",
    "100001111110111111100000011011111101",
    "111111000000100000001111011010000001",
    "100000011111101111101000011011011111",
    "101111110000001000000011111011000001",
    "100000000111111011111111111011001101",
    "111111111100000000000000000011111101",
    "1E0000000001111111111111111000000001",
    "111111111111111111111111111111111111",
]


    problem = parse_maze(maze_lines)
    dls_limit = problem.rows * problem.cols
    run_all(problem, dls_limit=dls_limit, ids_max_depth=None)


if __name__ == "__main__":
    main()
