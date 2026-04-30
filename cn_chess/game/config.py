from __future__ import annotations

import argparse
from dataclasses import dataclass

from cn_chess.core.enums import ControlType


@dataclass
class GameConfig:
    red_control: ControlType
    black_control: ControlType
    red_depth: int = 3
    black_depth: int = 3
    fps: int = 60
    ai_move_delay_ms: int = 250
    flip_view: bool = False


def _parse_control(value: str) -> ControlType:
    for control in ControlType:
        if control.value == value:
            return control
    raise ValueError(f"Unsupported control type: {value}")


def _mode_defaults(mode: str) -> tuple[ControlType, ControlType]:
    if mode == "human_vs_rule_ai":
        return ControlType.HUMAN, ControlType.RULE_AI
    if mode == "human_vs_alphabeta_ai":
        return ControlType.HUMAN, ControlType.ALPHABETA_AI
    if mode == "alphabeta_ai_vs_rule_ai":
        return ControlType.ALPHABETA_AI, ControlType.RULE_AI
    if mode == "ai_vs_ai":
        return ControlType.ALPHABETA_AI, ControlType.RULE_AI
    return ControlType.HUMAN, ControlType.RULE_AI


def parse_game_config() -> GameConfig:
    parser = argparse.ArgumentParser(description="Chinese chess (pygame)")
    parser.add_argument(
        "--mode",
        choices=[
            "human_vs_rule_ai",
            "human_vs_alphabeta_ai",
            "alphabeta_ai_vs_rule_ai",
            "ai_vs_ai",
            "custom",
        ],
        default="human_vs_rule_ai",
        help="Preset mode. Use --red/--black with custom mode.",
    )
    parser.add_argument(
        "--red",
        choices=[c.value for c in ControlType],
        default=None,
        help="Red control: human/rule_ai/alphabeta_ai.",
    )
    parser.add_argument(
        "--black",
        choices=[c.value for c in ControlType],
        default=None,
        help="Black control: human/rule_ai/alphabeta_ai.",
    )
    parser.add_argument("--depth", type=int, default=3, help="Default alpha-beta search depth.")
    parser.add_argument("--red-depth", type=int, default=None, help="Red alpha-beta search depth.")
    parser.add_argument("--black-depth", type=int, default=None, help="Black alpha-beta search depth.")
    parser.add_argument("--swap", action="store_true", help="Swap red/black control settings.")
    parser.add_argument("--flip-view", action="store_true", help="Flip board view.")
    parser.add_argument("--fps", type=int, default=60, help="Render FPS.")
    parser.add_argument("--ai-delay", type=int, default=250, help="AI move delay in milliseconds.")
    args = parser.parse_args()

    if args.mode == "custom":
        red = _parse_control(args.red or "human")
        black = _parse_control(args.black or "rule_ai")
    else:
        red, black = _mode_defaults(args.mode)
        if args.red is not None:
            red = _parse_control(args.red)
        if args.black is not None:
            black = _parse_control(args.black)

    if args.swap:
        red, black = black, red

    red_depth = args.red_depth if args.red_depth is not None else args.depth
    black_depth = args.black_depth if args.black_depth is not None else args.depth

    return GameConfig(
        red_control=red,
        black_control=black,
        red_depth=max(1, red_depth),
        black_depth=max(1, black_depth),
        fps=max(10, args.fps),
        ai_move_delay_ms=max(0, args.ai_delay),
        flip_view=args.flip_view,
    )
