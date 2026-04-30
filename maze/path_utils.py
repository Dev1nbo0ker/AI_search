from __future__ import annotations

from .models import Pos


def reconstruct_path(parent: dict[Pos, Pos | None], end: Pos) -> list[Pos]:
    if end not in parent:
        return []
    path: list[Pos] = []
    cur: Pos | None = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def merge_bidirectional_path(
    parent_fwd: dict[Pos, Pos | None],
    parent_bwd: dict[Pos, Pos | None],
    meet: Pos,
) -> list[Pos]:
    """Merge S->meet and meet->E, removing duplicate meet node."""
    start_to_meet = reconstruct_path(parent_fwd, meet)
    end_to_meet = reconstruct_path(parent_bwd, meet)
    meet_to_end = list(reversed(end_to_meet))
    return start_to_meet + meet_to_end[1:]
