from __future__ import annotations

from collections import deque

from ..constants import BLANK_ADJ, GOAL_STATE, PDB_PATTERNS, SIZE
from ..types import State
from .basic import manhattan_distance

_PDB_TABLES: dict[tuple[int, ...], bytearray] = {}
_PDB_INF = 255


def _encode_pattern_state(blank_pos: int, tile_positions: tuple[int, ...]) -> int:
    enc = blank_pos
    shift = 4
    for pos in tile_positions:
        enc |= pos << shift
        shift += 4
    return enc


def _encode_pattern_from_full_state(state: State, pattern: tuple[int, ...]) -> int:
    tile_to_pos = [0] * SIZE
    for idx, tile in enumerate(state):
        tile_to_pos[tile] = idx
    blank_pos = tile_to_pos[0]
    tile_positions = tuple(tile_to_pos[tile] for tile in pattern)
    return _encode_pattern_state(blank_pos, tile_positions)


def _build_single_pdb(pattern: tuple[int, ...]) -> bytearray:
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
            moved_shift = -1
            for i in range(k):
                shift = 4 * (i + 1)
                if ((enc >> shift) & 0xF) == nb:
                    moved_shift = shift
                    break

            new_enc = (enc & ~0xF) | nb
            if moved_shift == -1:
                weight = 0
            else:
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


def ensure_pdb_built() -> None:
    if _PDB_TABLES:
        return
    for pattern in PDB_PATTERNS:
        _PDB_TABLES[pattern] = _build_single_pdb(pattern)


def heuristic_pdb(state: State) -> int:
    ensure_pdb_built()
    h = 0
    for pattern in PDB_PATTERNS:
        enc = _encode_pattern_from_full_state(state, pattern)
        d = _PDB_TABLES[pattern][enc]
        if d == _PDB_INF:
            return manhattan_distance(state)
        h += d
    return h

