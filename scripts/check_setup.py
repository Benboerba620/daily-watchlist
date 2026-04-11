#!/usr/bin/env python3
"""
Daily Watchlist - 环境检查
"""

import os
import sys
from io import StringIO
from pathlib import Path

from workspace_paths import (
    CONFIG_FILE_CANDIDATES,
    ENV_FILE_CANDIDATES,
    WATCHLIST_FILE_CANDIDATES,
    resolve_config_path,
    resolve_env_path,
    resolve_watchlist_path,
)

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def check(name, passed, msg=""):
    status = OK if passed else FAIL
    detail = f" - {msg}" if msg else ""
    print(f"  {status} {name}{detail}")
    return passed


def load_env_file(env_file):
    from dotenv import dotenv_values

    raw_text = env_file.read_text(encoding="utf-8-sig")
    parsed = dotenv_values(stream=StringIO(raw_text))
    for key, value in parsed.items():
        if value is not None and key not in os.environ:
            os.environ[key] = value


def main():
    print("Daily Watchlist - 环境检查\n")
    all_pass = True

    version = sys.version_info
    all_pass &= check(
        "Python >= 3.10",
        version >= (3, 10),
        f"当前版本 {version.major}.{version.minor}.{version.micro}",
    )

    for pkg in ["requests", "dotenv", "yaml"]:
        try:
            __import__(pkg)
            check(f"依赖包: {pkg}", True)
        except ImportError:
            real_name = {"dotenv": "python-dotenv", "yaml": "pyyaml"}.get(pkg, pkg)
            all_pass &= check(f"依赖包: {pkg}", False, f"请执行 pip install {real_name}")

    root = Path(__file__).resolve().parent.parent
    config_dir = root / "config"
    env_file = resolve_env_path(config_dir)

    all_pass &= check("config/ 目录", config_dir.exists())

    if not env_file.exists():
        all_pass &= check(
            f"config/{ENV_FILE_CANDIDATES[0]}",
            False,
            f"请创建 {ENV_FILE_CANDIDATES[0]} 或重新运行安装器，然后填入 API key",
        )
    else:
        check(f"config/{env_file.name}", True)
        load_env_file(env_file)

        fmp_key = os.getenv("FMP_API_KEY", "")
        if not fmp_key or fmp_key.startswith("your_"):
            all_pass &= check("FMP_API_KEY", False, f"请在 config/{env_file.name} 中填写 FMP_API_KEY")
        else:
            try:
                import requests

                response = requests.get(
                    f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={fmp_key}",
                    timeout=10,
                )
                data = response.json()
                if isinstance(data, list) and data and "symbol" in data[0]:
                    check("FMP_API_KEY", True, f"可用（AAPL = ${data[0].get('price', '?')}）")
                else:
                    all_pass &= check("FMP_API_KEY", False, f"返回异常: {str(data)[:100]}")
            except Exception as exc:  # noqa: BLE001
                all_pass &= check("FMP_API_KEY", False, f"连接失败: {exc}")

        ts_token = os.getenv("TUSHARE_TOKEN", "")
        if ts_token and not ts_token.startswith("your_"):
            try:
                import tushare as ts

                pro = ts.pro_api(ts_token)
                pro.trade_cal(exchange="SSE", start_date="20260101", end_date="20260102")
                check("TUSHARE_TOKEN", True, "可用")
            except ImportError:
                print(f"  {WARN} 已设置 TUSHARE_TOKEN，但未安装 tushare（pip install tushare）")
            except Exception as exc:  # noqa: BLE001
                print(f"  {WARN} TUSHARE_TOKEN 检查跳过: {exc}")
        else:
            print(f"  {WARN} 未设置 TUSHARE_TOKEN（可选，仅 A 股 / 港股需要）")

    config_file = resolve_config_path(config_dir)
    if config_file.exists():
        check(f"config/{config_file.name}", True)
    else:
        all_pass &= check(
            f"config/{CONFIG_FILE_CANDIDATES[0]}",
            False,
            f"请创建 {CONFIG_FILE_CANDIDATES[0]} 或重新运行安装器",
        )

    watchlist_file = resolve_watchlist_path(config_dir)
    if watchlist_file.exists():
        check(f"config/{watchlist_file.name}", True)
    else:
        all_pass &= check(
            f"config/{WATCHLIST_FILE_CANDIDATES[0]}",
            False,
            f"请创建 {WATCHLIST_FILE_CANDIDATES[0]} 或通过 /dw-import 生成",
        )

    print()
    if all_pass:
        print("所有必需检查均已通过。现在可以运行 /dw-today 生成第一份简报。")
        sys.exit(0)

    print("存在未完成项。请按上面的提示修复后再运行。")
    print(f"常见下一步：编辑 config/{ENV_FILE_CANDIDATES[0]} 填入 FMP_API_KEY，然后重新运行本检查。")
    sys.exit(1)


if __name__ == "__main__":
    main()
