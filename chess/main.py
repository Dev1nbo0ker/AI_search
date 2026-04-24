from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chess.game.config import parse_game_config
from chess.game.controller import GameController


def main() -> None:
    config = parse_game_config()
    game = GameController(config)
    game.run()


if __name__ == "__main__":
    main()
