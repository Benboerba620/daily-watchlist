#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from generate_daily_report import build_report, load_config, load_template
from workspace_paths import resolve_config_dir, resolve_config_path, resolve_template_path


def build_stub_market_data() -> dict:
    return {
        "quotes": [
            {"ticker": "AAPL", "name": "Apple", "changesPercentage": 1.25},
            {"ticker": "MSFT", "name": "Microsoft", "changesPercentage": -0.85},
            {"ticker": "NVDA", "name": "NVIDIA", "changesPercentage": 4.75},
        ],
        "movers": [
            {
                "ticker": "NVDA",
                "name": "NVIDIA",
                "changesPercentage": 4.75,
                "category": "important",
            }
        ],
        "earnings": [
            {
                "ticker": "AAPL",
                "date": "2026-04-11",
                "eps": 1.62,
                "epsEstimated": 1.55,
            },
            {
                "ticker": "MSFT",
                "date": "2026-04-15",
                "eps": None,
                "epsEstimated": 3.02,
            },
        ],
    }


def build_stub_macro_data() -> dict:
    return {
        "sentiment": "Normal",
        "macro": {
            "VIX": {"price": 17.2, "change_pct": -1.4, "status": "Normal"},
            "SPY": {"price": 523.4, "change_pct": 0.6},
            "QQQ": {"price": 441.9, "change_pct": 1.1},
            "GLD": {"price": 228.2, "change_pct": 0.2},
            "CLUSD": {"price": 78.4, "change_pct": -0.5},
            "BTC": {"price": 81234.0, "change_pct": 2.4},
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline smoke test for report generation")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("."),
        help="Workspace root containing config/ and templates/",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace_root = args.workspace.resolve()
    config_dir = resolve_config_dir(workspace_root)
    config = load_config(resolve_config_path(config_dir))
    template_text = load_template(resolve_template_path(workspace_root))
    report_path = build_report(
        workspace_root,
        config,
        template_text,
        build_stub_market_data(),
        build_stub_macro_data(),
        [],
        [],
    )
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
