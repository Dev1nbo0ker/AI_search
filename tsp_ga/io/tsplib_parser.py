from __future__ import annotations

from tsp_ga.models import TSPInstance


def load_tsplib_euc2d(file_path: str) -> TSPInstance:
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    headers: dict[str, str] = {}
    coord_start = None

    for index, line in enumerate(lines):
        upper = line.upper()
        if upper == "NODE_COORD_SECTION":
            coord_start = index + 1
            break

        if ":" in line:
            key, value = line.split(":", maxsplit=1)
        else:
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            key, value = parts
        headers[key.strip().upper()] = value.strip()

    if coord_start is None:
        raise ValueError("Invalid TSPLIB file: missing NODE_COORD_SECTION.")

    edge_weight_type = headers.get("EDGE_WEIGHT_TYPE", "").upper()
    if edge_weight_type != "EUC_2D":
        raise ValueError(f"Only EDGE_WEIGHT_TYPE = EUC_2D is supported, got {edge_weight_type!r}.")

    name = headers.get("NAME", "UNKNOWN")
    dimension = int(headers["DIMENSION"])
    node_ids, coordinates = _parse_node_coord_section(lines[coord_start:])

    if len(coordinates) != dimension:
        raise ValueError(
            f"DIMENSION says {dimension}, but NODE_COORD_SECTION contains {len(coordinates)} cities."
        )

    return TSPInstance(
        name=name,
        dimension=dimension,
        node_ids=node_ids,
        coordinates=coordinates,
    )


def _parse_node_coord_section(lines: list[str]) -> tuple[list[int], list[tuple[float, float]]]:
    node_ids: list[int] = []
    coordinates: list[tuple[float, float]] = []

    for line in lines:
        upper = line.upper()
        if upper in {"EOF", "DISPLAY_DATA_SECTION"}:
            break

        parts = line.split()
        if len(parts) < 3:
            raise ValueError(f"Invalid coordinate line: {line!r}")

        node_id = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        node_ids.append(node_id)
        coordinates.append((x, y))

    return node_ids, coordinates

