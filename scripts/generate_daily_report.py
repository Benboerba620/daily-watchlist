from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values

from workspace_paths import (
    find_workspace_root,
    resolve_config_dir,
    resolve_config_path,
    resolve_env_path,
)


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def load_env_file(env_path: Path) -> dict[str, str]:
    raw_text = env_path.read_text(encoding="utf-8-sig")
    parsed = dotenv_values(stream=StringIO(raw_text))
    values: dict[str, str] = {}
    for key, value in parsed.items():
        if value is None:
            continue
        values[key] = value
        if key not in os.environ:
            os.environ[key] = value
    return values


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8-sig") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping in {config_path}")
    return payload


def run_json_script(workspace_root: Path, script_name: str) -> dict[str, Any]:
    script_path = workspace_root / "scripts" / script_name
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    if completed.stderr.strip():
        log(completed.stderr.strip())
    return json.loads(completed.stdout)


def format_pct(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):+.2f}%"


def format_num(value: Any, digits: int = 2, prefix: str = "") -> str:
    if value is None:
        return "N/A"
    if isinstance(value, int):
        return f"{prefix}{value}"
    if isinstance(value, float):
        return f"{prefix}{value:.{digits}f}"
    return f"{prefix}{value}"


def status_from_change(value: Any) -> str:
    if value is None:
        return "N/A"
    numeric = float(value)
    if numeric > 1:
        return "强势"
    if numeric > 0:
        return "上涨"
    if numeric < -1:
        return "偏弱"
    if numeric < 0:
        return "下跌"
    return "持平"


def build_report(workspace_root: Path, config: dict[str, Any], market_data: dict[str, Any], macro_data: dict[str, Any]) -> Path:
    today = date.today()
    weekday_map = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日",
    }
    weekday = weekday_map[today.strftime("%A")]
    report_dir = workspace_root / "daily-watchlist-reports" / today.strftime("%Y-%m")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{today.isoformat()}.md"

    macro = macro_data["macro"]
    quotes = market_data.get("quotes") or []
    movers = market_data.get("movers") or []
    earnings = market_data.get("earnings") or []
    other_movers = sorted(
        [item for item in quotes if item.get("changesPercentage") is not None],
        key=lambda item: abs(float(item["changesPercentage"])),
        reverse=True,
    )[:5]

    lines: list[str] = []
    lines.append(f"# 每日监控简报 - {today.isoformat()}（{weekday}）")
    lines.append("")
    lines.append("> 说明：本文件由本地脚本生成数据骨架。新闻检索、原因分析与主题研究应由 Claude Code 在运行 `/dw-today` 时通过 WebSearch 补充。")
    lines.append("")
    lines.append("## 市场概览")
    lines.append("")
    lines.append("| 指标 | 数值 | 涨跌 | 状态 |")
    lines.append("|------|------|------|------|")
    lines.append(f"| VIX | {format_num(macro['VIX']['price'])} | {format_pct(macro['VIX']['change_pct'])} | {macro['VIX']['status']} |")
    lines.append(f"| SPY | {format_num(macro['SPY']['price'])} | {format_pct(macro['SPY']['change_pct'])} | {status_from_change(macro['SPY']['change_pct'])} |")
    lines.append(f"| QQQ | {format_num(macro['QQQ']['price'])} | {format_pct(macro['QQQ']['change_pct'])} | {status_from_change(macro['QQQ']['change_pct'])} |")
    lines.append(f"| GLD | {format_num(macro['GLD']['price'])} | {format_pct(macro['GLD']['change_pct'])} | {status_from_change(macro['GLD']['change_pct'])} |")
    lines.append(f"| WTI | {format_num(macro['CLUSD']['price'])} | {format_pct(macro['CLUSD']['change_pct'])} | {status_from_change(macro['CLUSD']['change_pct'])} |")
    lines.append(f"| BTC | {format_num(macro['BTC']['price'], prefix='$')} | {format_pct(macro['BTC']['change_pct'])} | {status_from_change(macro['BTC']['change_pct'])} |")
    lines.append("")
    lines.append(f"市场情绪：{macro_data.get('sentiment', 'N/A')}。")
    lines.append("")
    lines.append("## 个股异动")
    lines.append("")
    lines.append("### 重点异动")
    lines.append("")
    lines.append("| Ticker | 名称 | 涨跌幅 | 分类 | 待补充 |")
    lines.append("|--------|------|--------|------|--------|")
    if movers:
        for mover in movers[:10]:
            lines.append(f"| {mover['ticker']} | {mover['name']} | {format_pct(mover['changesPercentage'])} | {mover['category']} | 用 WebSearch 补新闻与原因分析 |")
    else:
        lines.append("| 无 | 当前没有股票超过阈值 | N/A | N/A | 无需补充 |")
    lines.append("")
    lines.append("### 其他异动")
    lines.append("")
    lines.append("| Ticker | 名称 | 涨跌幅 |")
    lines.append("|--------|------|--------|")
    for mover in other_movers:
        lines.append(f"| {mover['ticker']} | {mover['name']} | {format_pct(mover['changesPercentage'])} |")
    lines.append("")
    lines.append("## 财报跟踪")
    lines.append("")
    lines.append("### 已披露")
    lines.append("")
    lines.append("| Ticker | 日期 | 预期 EPS | 实际 EPS | Surprise | 待补充 |")
    lines.append("|--------|------|----------|----------|----------|--------|")
    if earnings:
        for item in earnings[:10]:
            lines.append(f"| {item['ticker']} | {item.get('date') or 'N/A'} | {item.get('epsEstimated') or 'N/A'} | {item.get('eps') or 'N/A'} | N/A | 用 WebSearch 补市场反应 |")
    else:
        lines.append("| 无 | N/A | N/A | N/A | N/A | 当前没有财报条目 |")
    lines.append("")
    lines.append("### 本周待披露")
    lines.append("")
    lines.append("| Ticker | 日期 | 预期 EPS |")
    lines.append("|--------|------|----------|")
    lines.append("| 无 | N/A | N/A |")
    lines.append("")
    lines.append("## 重点主题")
    lines.append("")
    focus_areas = config.get("focus_areas") or []
    if focus_areas:
        for area in focus_areas[:3]:
            name = str(area.get("name") or "未命名主题")
            keywords = ", ".join(str(item) for item in area.get("keywords") or [])
            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- 关键词：{keywords}")
            lines.append("- 用 Claude Code WebSearch 进行主题新闻检索，并做来源核对后再写入。")
            lines.append("")
    else:
        lines.append("### 无")
        lines.append("")
        lines.append("- 当前配置没有 focus areas。")
        lines.append("")
    lines.append("## 信息来源")
    lines.append("")
    lines.append("- `fetch_market_data.py`：实时拉取监控池行情、异动和财报")
    lines.append("- `fetch_macro_data.py`：实时拉取 VIX、指数、商品和 BTC")
    lines.append("- 新闻部分：应由 Claude Code 通过 WebSearch 补充，不由本地 FMP 新闻接口代替")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    configure_stdio()
    script_dir = Path(__file__).resolve().parent
    workspace_root = find_workspace_root(script_dir)
    config_dir = resolve_config_dir(workspace_root)
    load_env_file(resolve_env_path(config_dir))
    config = load_config(resolve_config_path(config_dir))

    market_data = run_json_script(workspace_root, "fetch_market_data.py")
    macro_data = run_json_script(workspace_root, "fetch_macro_data.py")
    report_path = build_report(workspace_root, config, market_data, macro_data)
    print(json.dumps({"report_path": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
