from __future__ import annotations

import argparse
from dataclasses import dataclass

from chess.core.enums import ControlType


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
    parser = argparse.ArgumentParser(description="中国象棋（pygame）")
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
        help="预设模式（custom 时使用 --red/--black）",
    )
    parser.add_argument(
        "--red",
        choices=[c.value for c in ControlType],
        default=None,
        help="红方控制：human/rule_ai/alphabeta_ai",
    )
    parser.add_argument(
        "--black",
        choices=[c.value for c in ControlType],
        default=None,
        help="黑方控制：human/rule_ai/alphabeta_ai",
    )
    parser.add_argument("--depth", type=int, default=3, help="alpha-beta 默认深度")
    parser.add_argument("--red-depth", type=int, default=None, help="红方 alpha-beta 搜索深度")
    parser.add_argument("--black-depth", type=int, default=None, help="黑方 alpha-beta 搜索深度")
    parser.add_argument("--swap", action="store_true", help="红黑控制方式互换")
    parser.add_argument("--flip-view", action="store_true", help="翻转棋盘视角（黑方在下）")
    parser.add_argument("--fps", type=int, default=60, help="渲染帧率")
    parser.add_argument("--ai-delay", type=int, default=250, help="AI 落子间隔毫秒")
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

