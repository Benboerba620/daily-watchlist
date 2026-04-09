from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Iterable

import requests
import yaml
from dotenv import dotenv_values
from workspace_paths import (
    find_workspace_root,
    resolve_config_dir,
    resolve_config_path,
    resolve_env_path,
    resolve_watchlist_path,
)

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
DEFAULT_TIMEOUT = 20
DEFAULT_THRESHOLDS = {
    "large_cap_move": 3.0,
    "small_cap_move": 7.0,
}
WATCHLIST_COLUMNS = ("ticker", "name", "market", "market cap", "category")
CN_SUFFIXES = (".SH", ".SZ")
HK_SUFFIX = ".HK"


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)

def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {config_path}")
    return data


def load_env_file(env_path: Path) -> None:
    raw_text = env_path.read_text(encoding="utf-8-sig")
    parsed = dotenv_values(stream=StringIO(raw_text))
    for key, value in parsed.items():
        if value is not None and key not in os.environ:
            os.environ[key] = value


def load_env(env_path: Path) -> dict[str, str]:
    if env_path.is_file():
        load_env_file(env_path)
    else:
        log(f"Warning: {env_path} not found")
    return {
        "FMP_API_KEY": os.environ.get("FMP_API_KEY", "").strip(),
        "TUSHARE_TOKEN": os.environ.get("TUSHARE_TOKEN", "").strip(),
    }


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def parse_markdown_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: Iterable[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_watchlist(watchlist_path: Path) -> list[dict[str, str]]:
    if not watchlist_path.is_file():
        raise FileNotFoundError(f"Watchlist file not found: {watchlist_path}")

    entries: list[dict[str, str]] = []
    headers: list[str] | None = None

    with watchlist_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            cells = parse_markdown_row(line)
            if cells is None:
                headers = None
                continue

            normalized = [normalize_header(cell) for cell in cells]
            if headers is None:
                if tuple(normalized) == WATCHLIST_COLUMNS:
                    headers = list(normalized)
                continue

            if is_separator_row(cells):
                continue

            if len(cells) != len(headers):
                log(
                    f"Warning: skipping malformed watchlist row at {watchlist_path}:{line_number}"
                )
                continue

            row = dict(zip(headers, cells))
            ticker = row["ticker"].strip().upper()
            if not ticker:
                continue

            entries.append(
                {
                    "ticker": ticker,
                    "name": row["name"].strip(),
                    "market": row["market"].strip(),
                    "market_cap": row["market cap"].strip(),
                    "category": row["category"].strip(),
                }
            )

    if not entries:
        log(f"Warning: no watchlist entries found in {watchlist_path}")
    return entries


def chunked(items: list[str], size: int) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def request_json(url: str) -> Any:
    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_fmp_quote_batch(tickers: list[str], api_key: str) -> list[dict[str, Any]]:
    joined = ",".join(tickers)
    url = f"{FMP_BASE_URL}/quote/{joined}?apikey={api_key}"
    payload = request_json(url)
    if isinstance(payload, list):
        return payload
    log(f"Warning: unexpected FMP quote response for {joined}: {payload}")
    return []


def fetch_fmp_quotes(tickers: list[str], api_key: str, max_workers: int) -> list[dict[str, Any]]:
    if not tickers:
        return []
    if not api_key:
        log("Warning: FMP_API_KEY not set, skipping FMP quote requests")
        return []

    quotes: list[dict[str, Any]] = []
    batches = chunked(tickers, 50)
    with ThreadPoolExecutor(max_workers=min(max_workers, len(batches))) as executor:
        futures = {
            executor.submit(fetch_fmp_quote_batch, batch, api_key): batch for batch in batches
        }
        for future in as_completed(futures):
            batch = futures[future]
            try:
                quotes.extend(future.result())
            except Exception as exc:  # noqa: BLE001
                log(f"Warning: failed to fetch FMP quotes for {','.join(batch)}: {exc}")
    return quotes


def load_tushare_client(token: str) -> Any | None:
    if not token:
        return None
    try:
        import tushare as ts  # type: ignore
    except ImportError as exc:
        log(f"Warning: tushare is not installed, skipping CN/HK quotes: {exc}")
        return None

    try:
        return ts.pro_api(token)
    except Exception as exc:  # noqa: BLE001
        log(f"Warning: failed to initialize tushare client: {exc}")
        return None


def fetch_tushare_quote(client: Any, ticker: str) -> dict[str, Any] | None:
    end_date = date.today()
    start_date = end_date - timedelta(days=10)
    start_text = start_date.strftime("%Y%m%d")
    end_text = end_date.strftime("%Y%m%d")
    try:
        if ticker.endswith(CN_SUFFIXES):
            frame = client.daily(ts_code=ticker, start_date=start_text, end_date=end_text)
        elif ticker.endswith(HK_SUFFIX):
            frame = client.hk_daily(ts_code=ticker, start_date=start_text, end_date=end_text)
        else:
            return None
    except Exception as exc:  # noqa: BLE001
        log(f"Warning: tushare request failed for {ticker}: {exc}")
        return None

    if frame is None or frame.empty:
        log(f"Warning: tushare returned no data for {ticker}")
        return None

    latest = frame.sort_values("trade_date", ascending=False).iloc[0]
    return {
        "symbol": ticker,
        "price": parse_float(latest.get("close")),
        "change": parse_float(latest.get("change")),
        "changesPercentage": parse_float(latest.get("pct_chg")),
        "previousClose": parse_float(latest.get("pre_close")),
        "open": parse_float(latest.get("open")),
        "dayHigh": parse_float(latest.get("high")),
        "dayLow": parse_float(latest.get("low")),
        "volume": parse_float(latest.get("vol")),
        "tradeDate": str(latest.get("trade_date", "")),
        "source": "tushare",
    }


def fetch_tushare_quotes(
    tickers: list[str], token: str, max_workers: int
) -> list[dict[str, Any]]:
    if not tickers:
        return []
    if not token:
        log("Warning: TUSHARE_TOKEN not set, skipping CN/HK quotes")
        return []

    client = load_tushare_client(token)
    if client is None:
        return []

    quotes: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        futures = {executor.submit(fetch_tushare_quote, client, ticker): ticker for ticker in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                payload = future.result()
                if payload:
                    quotes.append(payload)
            except Exception as exc:  # noqa: BLE001
                log(f"Warning: failed to fetch tushare quote for {ticker}: {exc}")
    return quotes


def build_quote_record(
    raw_quote: dict[str, Any],
    watchlist_entry: dict[str, str],
) -> dict[str, Any]:
    ticker = watchlist_entry["ticker"]
    return {
        "ticker": ticker,
        "name": watchlist_entry["name"] or raw_quote.get("name", ""),
        "market": watchlist_entry["market"],
        "marketCapCategory": watchlist_entry["market_cap"],
        "category": watchlist_entry["category"],
        "price": parse_float(raw_quote.get("price")),
        "change": parse_float(raw_quote.get("change")),
        "changesPercentage": parse_float(raw_quote.get("changesPercentage")),
        "previousClose": parse_float(raw_quote.get("previousClose")),
        "open": parse_float(raw_quote.get("open")),
        "dayHigh": parse_float(raw_quote.get("dayHigh")),
        "dayLow": parse_float(raw_quote.get("dayLow")),
        "volume": parse_float(raw_quote.get("volume")),
        "tradeDate": raw_quote.get("tradeDate") or raw_quote.get("timestamp"),
        "source": raw_quote.get("source", "fmp"),
    }


def find_movers(
    quotes: list[dict[str, Any]], thresholds: dict[str, float]
) -> list[dict[str, Any]]:
    movers: list[dict[str, Any]] = []
    large_threshold = float(thresholds.get("large_cap_move", DEFAULT_THRESHOLDS["large_cap_move"]))
    small_threshold = float(thresholds.get("small_cap_move", DEFAULT_THRESHOLDS["small_cap_move"]))

    for quote in quotes:
        change_pct = parse_float(quote.get("changesPercentage"))
        if change_pct is None:
            continue
        threshold = (
            large_threshold
            if quote.get("marketCapCategory", "").strip().lower() == "large"
            else small_threshold
        )
        if abs(change_pct) >= threshold:
            movers.append({**quote, "threshold": threshold})
    return movers


def week_bounds(today: date) -> tuple[date, date]:
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


def fetch_earnings_calendar(
    api_key: str, watchlist_map: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    if not api_key:
        log("Warning: FMP_API_KEY not set, skipping earnings calendar")
        return []

    monday, friday = week_bounds(date.today())
    url = (
        f"{FMP_BASE_URL}/earning_calendar"
        f"?from={monday.isoformat()}&to={friday.isoformat()}&apikey={api_key}"
    )

    try:
        payload = request_json(url)
    except Exception as exc:  # noqa: BLE001
        log(f"Warning: failed to fetch earnings calendar: {exc}")
        return []

    if not isinstance(payload, list):
        log(f"Warning: unexpected FMP earnings response: {payload}")
        return []

    results: list[dict[str, Any]] = []
    for item in payload:
        symbol = str(item.get("symbol", "")).strip().upper()
        if symbol not in watchlist_map:
            continue
        watch = watchlist_map[symbol]
        results.append(
            {
                "ticker": symbol,
                "name": watch["name"],
                "market": watch["market"],
                "category": watch["category"],
                "date": item.get("date"),
                "time": item.get("time"),
                "eps": parse_float(item.get("eps")),
                "epsEstimated": parse_float(item.get("epsEstimated")),
                "revenue": parse_float(item.get("revenue")),
                "revenueEstimated": parse_float(item.get("revenueEstimated")),
            }
        )

    results.sort(key=lambda row: (row.get("date") or "", row["ticker"]))
    return results


def fetch_profile(ticker: str, api_key: str) -> list[dict[str, Any]]:
    url = f"{FMP_BASE_URL}/profile/{ticker}?apikey={api_key}"
    payload = request_json(url)
    if isinstance(payload, list):
        return payload
    log(f"Warning: unexpected FMP profile response for {ticker}: {payload}")
    return []


def classify_market_cap(mkt_cap: Any) -> str:
    if not isinstance(mkt_cap, (int, float)):
        return ""
    if mkt_cap > 10_000_000_000:
        return "Large"
    if mkt_cap > 2_000_000_000:
        return "Mid"
    return "Small"


def normalize_profile(raw: dict[str, Any], requested_ticker: str) -> dict[str, Any]:
    return {
        "ticker": raw.get("symbol", requested_ticker),
        "name": raw.get("companyName", ""),
        "sector": raw.get("sector", "Unknown"),
        "industry": raw.get("industry", ""),
        "market_cap": raw.get("mktCap", 0),
        "cap_label": classify_market_cap(raw.get("mktCap")),
        "exchange": raw.get("exchangeShortName", ""),
        "country": raw.get("country", ""),
    }


def fetch_profiles(tickers: list[str], api_key: str, max_workers: int) -> list[dict[str, Any]]:
    if not api_key:
        raise RuntimeError("FMP_API_KEY is required for --profile mode")
    if not tickers:
        return []

    profiles: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(tickers))) as executor:
        futures = {executor.submit(fetch_profile, ticker, api_key): ticker for ticker in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                raw_list = future.result()
                if raw_list:
                    profiles.append(normalize_profile(raw_list[0], ticker))
                else:
                    profiles.append({"ticker": ticker, "name": "", "sector": "Unrecognized", "error": "Not found in FMP"})
            except Exception as exc:  # noqa: BLE001
                log(f"Warning: failed to fetch profile for {ticker}: {exc}")
                profiles.append({"ticker": ticker, "name": "", "sector": "Unrecognized", "error": str(exc)})
    return sorted(profiles, key=lambda item: str(item.get("ticker", "")))


def parse_requested_tickers(value: str) -> list[str]:
    tickers = [token.strip().upper() for token in re.split(r"[\s,]+", value) if token.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for ticker in tickers:
        if ticker not in seen:
            seen.add(ticker)
            deduped.append(ticker)
    return deduped


def build_snapshot(
    watchlist: list[dict[str, str]],
    api_key: str,
    tushare_token: str,
    thresholds: dict[str, float],
    max_workers: int,
) -> dict[str, Any]:
    watchlist_map = {item["ticker"]: item for item in watchlist}
    fmp_tickers = [
        item["ticker"]
        for item in watchlist
        if not item["ticker"].endswith(CN_SUFFIXES) and not item["ticker"].endswith(HK_SUFFIX)
    ]
    tushare_tickers = [
        item["ticker"]
        for item in watchlist
        if item["ticker"].endswith(CN_SUFFIXES) or item["ticker"].endswith(HK_SUFFIX)
    ]

    quotes: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        quote_future = executor.submit(fetch_fmp_quotes, fmp_tickers, api_key, max_workers)
        tushare_future = executor.submit(
            fetch_tushare_quotes, tushare_tickers, tushare_token, max_workers
        )
        earnings_future = executor.submit(fetch_earnings_calendar, api_key, watchlist_map)

        fmp_quotes = quote_future.result()
        tushare_quotes = tushare_future.result()
        earnings = earnings_future.result()

    for raw in fmp_quotes:
        symbol = str(raw.get("symbol", "")).strip().upper()
        if symbol in watchlist_map:
            quotes.append(build_quote_record(raw, watchlist_map[symbol]))

    for raw in tushare_quotes:
        symbol = str(raw.get("symbol", "")).strip().upper()
        if symbol in watchlist_map:
            quotes.append(build_quote_record(raw, watchlist_map[symbol]))

    quotes.sort(key=lambda row: row["ticker"])
    fetched_tickers = {quote["ticker"] for quote in quotes}
    missing_quotes = [item["ticker"] for item in watchlist if item["ticker"] not in fetched_tickers]
    if missing_quotes:
        log(f"Warning: no quote data returned for: {', '.join(missing_quotes)}")
    movers = sorted(find_movers(quotes, thresholds), key=lambda row: abs(row["changesPercentage"]), reverse=True)
    return {
        "quotes": quotes,
        "movers": movers,
        "earnings": earnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch watchlist quotes, movers, and earnings")
    parser.add_argument(
        "--profile",
        metavar="TICKERS",
        help="Comma-separated tickers to fetch from FMP profile endpoint instead of quote mode",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Maximum worker threads for parallel API calls",
    )
    return parser


def main() -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args()

    try:
        script_dir = Path(__file__).resolve().parent
        workspace_root = find_workspace_root(script_dir)
        config_dir = resolve_config_dir(workspace_root)
        config = load_config(resolve_config_path(config_dir))
        env = load_env(resolve_env_path(config_dir))
    except Exception as exc:  # noqa: BLE001
        log(f"Error: {exc}")
        return 1

    api_key = env["FMP_API_KEY"]
    tushare_token = env["TUSHARE_TOKEN"]
    config_thresholds = config.get("thresholds") or {}
    if not isinstance(config_thresholds, dict):
        log("Warning: config.thresholds is not a mapping, using defaults")
        config_thresholds = {}
    thresholds = {
        **DEFAULT_THRESHOLDS,
        **config_thresholds,
    }

    try:
        if args.profile:
            tickers = parse_requested_tickers(args.profile)
            payload = {"profiles": fetch_profiles(tickers, api_key, max(args.max_workers, 1))}
        else:
            watchlist = parse_watchlist(resolve_watchlist_path(config_dir))
            payload = build_snapshot(
                watchlist=watchlist,
                api_key=api_key,
                tushare_token=tushare_token,
                thresholds=thresholds,
                max_workers=max(args.max_workers, 1),
            )
    except Exception as exc:  # noqa: BLE001
        log(f"Error: {exc}")
        return 1

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
