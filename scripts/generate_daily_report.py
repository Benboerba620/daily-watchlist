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
    resolve_template_path,
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


def translate_sentiment(value: Any) -> str:
    if value is None:
        return "N/A"

    mapping = {
        "Optimistic": "乐观",
        "Normal": "中性",
        "Cautious": "谨慎",
        "Panic": "恐慌",
        "Unknown": "未知",
        "risk-on": "风险偏好回升",
        "risk-off": "风险偏好下降",
    }
    text = str(value).strip()
    if not text:
        return "N/A"
    parts = [part.strip() for part in text.split(",")]
    translated = [mapping.get(part, part) for part in parts]
    return "，".join(translated)


class SafeFormatDict(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def normalize_modules(config: dict[str, Any]) -> dict[str, bool]:
    modules = config.get("modules") or {}
    if not isinstance(modules, dict):
        modules = {}
    return {
        "macro": bool(modules.get("macro", True)),
        "earnings": bool(modules.get("earnings", True)),
        "focus_areas": bool(modules.get("focus_areas", True)),
    }


def build_macro_defaults() -> dict[str, dict[str, Any]]:
    return {
        "VIX": {"price": None, "change_pct": None, "status": "N/A"},
        "SPY": {"price": None, "change_pct": None},
        "QQQ": {"price": None, "change_pct": None},
        "GLD": {"price": None, "change_pct": None},
        "CLUSD": {"price": None, "change_pct": None},
        "BTC": {"price": None, "change_pct": None},
    }


def render_market_overview(macro_data: dict[str, Any], enabled: bool) -> tuple[str, str]:
    macro = build_macro_defaults()
    if enabled:
        macro.update(macro_data.get("macro") or {})
        summary = translate_sentiment(macro_data.get("sentiment") or "N/A")
    else:
        summary = "宏观模块已关闭。"

    rows = [
        "| 指标 | 数值 | 涨跌 | 状态 |",
        "|------|------|------|------|",
        f"| VIX | {format_num(macro['VIX'].get('price'))} | {format_pct(macro['VIX'].get('change_pct'))} | {translate_sentiment(macro['VIX'].get('status', 'N/A'))} |",
        f"| SPY | {format_num(macro['SPY'].get('price'))} | {format_pct(macro['SPY'].get('change_pct'))} | {status_from_change(macro['SPY'].get('change_pct'))} |",
        f"| QQQ | {format_num(macro['QQQ'].get('price'))} | {format_pct(macro['QQQ'].get('change_pct'))} | {status_from_change(macro['QQQ'].get('change_pct'))} |",
        f"| GLD | {format_num(macro['GLD'].get('price'))} | {format_pct(macro['GLD'].get('change_pct'))} | {status_from_change(macro['GLD'].get('change_pct'))} |",
        f"| WTI | {format_num(macro['CLUSD'].get('price'))} | {format_pct(macro['CLUSD'].get('change_pct'))} | {status_from_change(macro['CLUSD'].get('change_pct'))} |",
        f"| BTC | {format_num(macro['BTC'].get('price'), prefix='$')} | {format_pct(macro['BTC'].get('change_pct'))} | {status_from_change(macro['BTC'].get('change_pct'))} |",
    ]
    return "\n".join(rows), summary


def render_key_movers(movers: list[dict[str, Any]]) -> str:
    rows = [
        "| Ticker | 名称 | 涨跌幅 | 分类 | 摘要 |",
        "|--------|------|--------|------|------|",
    ]
    if movers:
        for mover in movers[:10]:
            rows.append(
                f"| {mover['ticker']} | {mover['name']} | {format_pct(mover['changesPercentage'])} | "
                f"{mover['category']} | 用 WebSearch 补新闻与原因分析 |"
            )
    else:
        rows.append("| 无 | 当前没有股票超过阈值 | N/A | N/A | 无需补充 |")
    return "\n".join(rows)


def render_other_movers(quotes: list[dict[str, Any]]) -> str:
    rows = [
        "| Ticker | 名称 | 涨跌幅 |",
        "|--------|------|--------|",
    ]
    other_movers = sorted(
        [item for item in quotes if item.get("changesPercentage") is not None],
        key=lambda item: abs(float(item["changesPercentage"])),
        reverse=True,
    )[:5]
    if other_movers:
        for mover in other_movers:
            rows.append(
                f"| {mover['ticker']} | {mover['name']} | {format_pct(mover['changesPercentage'])} |"
            )
    else:
        rows.append("| 无 | 当前没有可展示的异动 | N/A |")
    return "\n".join(rows)


def render_earnings_sections(earnings: list[dict[str, Any]], enabled: bool) -> tuple[str, str]:
    reported_rows = [
        "| Ticker | 日期 | 预期 EPS | 实际 EPS | Surprise | 市场反应 |",
        "|--------|------|----------|----------|----------|----------|",
    ]
    upcoming_rows = [
        "| Ticker | 日期 | 预期 EPS |",
        "|--------|------|----------|",
    ]
    if not enabled:
        reported_rows.append("| 模块关闭 | N/A | N/A | N/A | N/A | 财报模块已关闭，不生成财报骨架 |")
        upcoming_rows.append("| 模块关闭 | N/A | N/A |")
        return "\n".join(reported_rows), "\n".join(upcoming_rows)

    if earnings:
        for item in earnings[:10]:
            actual_eps = item.get("eps")
            estimated_eps = item.get("epsEstimated")
            surprise = (
                format_num(actual_eps - estimated_eps, digits=2)
                if isinstance(actual_eps, (int, float)) and isinstance(estimated_eps, (int, float))
                else "N/A"
            )
            target_rows = reported_rows if actual_eps is not None else upcoming_rows
            if actual_eps is not None:
                target_rows.append(
                    f"| {item['ticker']} | {item.get('date') or 'N/A'} | {estimated_eps if estimated_eps is not None else 'N/A'} | "
                    f"{actual_eps} | {surprise} | 用 WebSearch 补市场反应 |"
                )
            else:
                upcoming_rows.append(
                    f"| {item['ticker']} | {item.get('date') or 'N/A'} | {estimated_eps if estimated_eps is not None else 'N/A'} |"
                )

    if len(reported_rows) == 2:
        reported_rows.append("| 无 | N/A | N/A | N/A | N/A | 当前没有已披露财报条目 |")
    if len(upcoming_rows) == 2:
        upcoming_rows.append("| 无 | N/A | N/A |")
    return "\n".join(reported_rows), "\n".join(upcoming_rows)


def render_themes(config: dict[str, Any], enabled: bool) -> str:
    if not enabled:
        return "### 模块关闭\n\n- `focus_areas` 模块已关闭。"

    focus_areas = config.get("focus_areas") or []
    if not focus_areas:
        return "### 无\n\n- 当前配置没有 focus areas。"

    blocks: list[str] = []
    for area in focus_areas[:3]:
        name = str(area.get("name") or "未命名主题")
        keywords = ", ".join(str(item) for item in area.get("keywords") or [])
        blocks.append(f"### {name}")
        blocks.append("")
        blocks.append(f"- 关键词：{keywords or '未配置'}")
        blocks.append("- 用 Claude Code WebSearch 进行主题新闻检索，并做来源核对后再写入。")
        blocks.append("")
    return "\n".join(blocks).rstrip()


def render_sources(modules: dict[str, bool]) -> str:
    lines = ["- `fetch_market_data.py`：实时拉取监控池行情、异动和财报"]
    if modules["macro"]:
        lines.append("- `fetch_macro_data.py`：实时拉取 VIX、指数、商品和 BTC")
    else:
        lines.append("- `fetch_macro_data.py`：当前配置已关闭宏观模块，本次未调用")
    lines.append("- 新闻部分：应由 Claude Code 通过 WebSearch 补充，不由本地 FMP 新闻接口代替")
    return "\n".join(lines)


def load_template(template_path: Path) -> str:
    return template_path.read_text(encoding="utf-8-sig")


def build_report(
    workspace_root: Path,
    config: dict[str, Any],
    template_text: str,
    market_data: dict[str, Any],
    macro_data: dict[str, Any],
) -> Path:
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

    modules = normalize_modules(config)
    quotes = market_data.get("quotes") or []
    movers = market_data.get("movers") or []
    earnings = market_data.get("earnings") or []
    market_table, market_summary = render_market_overview(macro_data, modules["macro"])
    earnings_reported, earnings_upcoming = render_earnings_sections(
        earnings, modules["earnings"]
    )
    context = SafeFormatDict(
        DATE=today.isoformat(),
        WEEKDAY=weekday,
        REPORT_NOTE=(
            "> 说明：本文件由本地脚本生成数据骨架。新闻检索、原因分析与主题研究应由 "
            "Claude Code 在运行 `/dw-today` 时通过 WebSearch 补充。"
        ),
        MARKET_OVERVIEW_TABLE=market_table,
        MARKET_SUMMARY=market_summary,
        KEY_MOVERS_TABLE=render_key_movers(movers),
        OTHER_MOVERS_TABLE=render_other_movers(quotes),
        EARNINGS_REPORTED_TABLE=earnings_reported,
        EARNINGS_UPCOMING_TABLE=earnings_upcoming,
        THEMES_SECTION=render_themes(config, modules["focus_areas"]),
        SOURCES_SECTION=render_sources(modules),
    )
    rendered = template_text.format_map(context).rstrip() + "\n"
    report_path.write_text(rendered, encoding="utf-8")
    return report_path


def main() -> int:
    configure_stdio()
    script_dir = Path(__file__).resolve().parent
    workspace_root = find_workspace_root(script_dir)
    config_dir = resolve_config_dir(workspace_root)
    load_env_file(resolve_env_path(config_dir))
    config = load_config(resolve_config_path(config_dir))
    modules = normalize_modules(config)
    template_text = load_template(resolve_template_path(workspace_root))

    market_data = run_json_script(workspace_root, "fetch_market_data.py")
    macro_data = (
        run_json_script(workspace_root, "fetch_macro_data.py") if modules["macro"] else {}
    )
    report_path = build_report(workspace_root, config, template_text, market_data, macro_data)
    print(json.dumps({"report_path": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
