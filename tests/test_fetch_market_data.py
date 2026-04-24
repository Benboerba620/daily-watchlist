from __future__ import annotations

import builtins
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import fetch_market_data as fmd


class FetchMarketDataFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        fmd._YFINANCE_IMPORT_WARNING_EMITTED = False


    def test_parse_watchlist_keeps_optional_thesis_columns(self) -> None:
        watchlist_path = REPO_ROOT / "_tmp_watchlist_test.md"
        watchlist_path.write_text(
            "| Ticker | Name | Market | Market Cap | Category | Tier | Hypothesis | Notes |\n"
            "|------|------|------|----------|------|------|------------|-------|\n"
            "| NVDA | NVIDIA | US | Large | Technology | HOT | H1 | GPU bellwether |\n",
            encoding="utf-8",
        )
        try:
            entries = fmd.parse_watchlist(watchlist_path)
        finally:
            watchlist_path.unlink(missing_ok=True)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["ticker"], "NVDA")
        self.assertEqual(entries[0]["tier"], "HOT")
        self.assertEqual(entries[0]["hypothesis"], "H1")
        self.assertEqual(entries[0]["notes"], "GPU bellwether")

    def test_parse_watchlist_accepts_legacy_five_columns(self) -> None:
        watchlist_path = REPO_ROOT / "_tmp_watchlist_legacy_test.md"
        watchlist_path.write_text(
            "| Ticker | Name | Market | Market Cap | Category |\n"
            "|------|------|------|----------|------|\n"
            "| AAPL | Apple | US | Large | Technology |\n",
            encoding="utf-8",
        )
        try:
            entries = fmd.parse_watchlist(watchlist_path)
        finally:
            watchlist_path.unlink(missing_ok=True)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["tier"], "")
        self.assertEqual(entries[0]["hypothesis"], "")

    def test_fetch_stooq_quote_parses_csv(self) -> None:
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.text = (
            "Symbol,Date,Time,Open,High,Low,Close,Volume,Prev\n"
            "AAPL.US,2026-04-15,22:00:18,258.16,266.56,257.81,266.43,49913510,258.83\n"
        )

        with mock.patch.object(fmd.requests, "get", return_value=response) as get_mock:
            quote = fmd.fetch_stooq_quote("AAPL", "US")

        self.assertEqual(
            get_mock.call_args.args[0],
            "https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcvp&h&e=csv",
        )
        self.assertIsNotNone(quote)
        assert quote is not None
        self.assertEqual(quote["source"], "stooq")
        self.assertEqual(quote["tradeDate"], "2026-04-15")
        self.assertAlmostEqual(quote["price"], 266.43)
        self.assertAlmostEqual(quote["previousClose"], 258.83)
        self.assertAlmostEqual(quote["change"], 7.60)
        self.assertAlmostEqual(quote["changesPercentage"], 2.9362902291)

    def test_fetch_fallback_quote_stops_after_stooq_success(self) -> None:
        item = {"ticker": "AAPL", "market": "US"}
        env = {
            "FINNHUB_API_KEY": "finnhub-key",
            "EOD_API_KEY": "eod-key",
            "ENABLE_YFINANCE": "1",
        }
        stooq_quote = {"symbol": "AAPL", "price": 123.45, "source": "stooq"}

        with mock.patch.object(fmd, "fetch_stooq_quote", return_value=stooq_quote) as stooq_mock, \
            mock.patch.object(fmd, "fetch_finnhub_quote") as finnhub_mock, \
            mock.patch.object(fmd, "fetch_eod_quote") as eod_mock, \
            mock.patch.object(fmd, "fetch_yfinance_quote") as yfinance_mock:
            result = fmd.fetch_fallback_quote(item, env)

        self.assertEqual(result, stooq_quote)
        stooq_mock.assert_called_once_with("AAPL", "US")
        finnhub_mock.assert_not_called()
        eod_mock.assert_not_called()
        yfinance_mock.assert_not_called()

    def test_fetch_fallback_quote_uses_finnhub_after_stooq_miss(self) -> None:
        item = {"ticker": "AAPL", "market": "US"}
        env = {"FINNHUB_API_KEY": "finnhub-key", "ENABLE_YFINANCE": ""}
        finnhub_quote = {"symbol": "AAPL", "price": 200.0, "source": "finnhub"}

        with mock.patch.object(fmd, "fetch_stooq_quote", return_value=None), \
            mock.patch.object(fmd, "fetch_finnhub_quote", return_value=finnhub_quote) as finnhub_mock, \
            mock.patch.object(fmd, "fetch_eod_quote") as eod_mock, \
            mock.patch.object(fmd, "fetch_yfinance_quote") as yfinance_mock:
            result = fmd.fetch_fallback_quote(item, env)

        self.assertEqual(result, finnhub_quote)
        finnhub_mock.assert_called_once_with("AAPL", "finnhub-key")
        eod_mock.assert_not_called()
        yfinance_mock.assert_not_called()

    def test_fetch_fallback_quote_uses_eod_for_supported_market(self) -> None:
        item = {"ticker": "0700.HK", "market": "HK"}
        env = {"EOD_API_KEY": "eod-key", "ENABLE_YFINANCE": ""}
        eod_quote = {"symbol": "0700.HK", "price": 345.6, "source": "eod"}

        with mock.patch.object(fmd, "fetch_stooq_quote", return_value=None), \
            mock.patch.object(fmd, "fetch_finnhub_quote") as finnhub_mock, \
            mock.patch.object(fmd, "fetch_eod_quote", return_value=eod_quote) as eod_mock, \
            mock.patch.object(fmd, "fetch_yfinance_quote") as yfinance_mock:
            result = fmd.fetch_fallback_quote(item, env)

        self.assertEqual(result, eod_quote)
        finnhub_mock.assert_not_called()
        eod_mock.assert_called_once_with("0700.HK", "HK", "eod-key")
        yfinance_mock.assert_not_called()

    def test_fetch_yfinance_quote_logs_missing_dependency_once(self) -> None:
        original_import = builtins.__import__

        def fake_import(
            name: str,
            globals_: dict | None = None,
            locals_: dict | None = None,
            fromlist: tuple[str, ...] = (),
            level: int = 0,
        ):
            if name == "yfinance":
                raise ImportError("No module named 'yfinance'")
            return original_import(name, globals_, locals_, fromlist, level)

        with mock.patch("builtins.__import__", side_effect=fake_import), \
            mock.patch.object(fmd, "log") as log_mock:
            self.assertIsNone(fmd.fetch_yfinance_quote("AAPL"))
            self.assertIsNone(fmd.fetch_yfinance_quote("MSFT"))

        log_mock.assert_called_once()
        self.assertIn("ENABLE_YFINANCE is set but yfinance is not installed", log_mock.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
