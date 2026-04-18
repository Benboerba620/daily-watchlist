---
description: 批量导入 ticker 到 Daily Watchlist 监控池
argument-hint: [tickers...]
---

批量导入 ticker 到监控池。
用户输入：`$ARGUMENTS`

## 工作流

1. 解析用户输入，支持逗号、换行、空格分隔。
2. 统一转为大写并去重。
3. 运行以下命令查询公司资料：
   - `python scripts/fetch_market_data.py --profile TICKER1,TICKER2`
4. 按行业和市值级别分类。
5. 向用户展示准备写入的 watchlist 内容，等待确认。
6. 确认后写入 `config/daily-watchlist-watchlist.md`。

如果工作区仍然使用旧文件 `config/watchlist.md`，可以继续兼容读取，但保存时优先写入 namespaced 文件。
