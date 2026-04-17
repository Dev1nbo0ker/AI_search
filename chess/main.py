from __future__ import annotations

from AI_search.chess.game.config import parse_game_config
from AI_search.chess.game.controller import GameController


def main() -> None:
    config = parse_game_config()
    game = GameController(config)
    game.run()


if __name__ == "__main__":
    main()
