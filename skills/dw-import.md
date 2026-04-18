# Daily Watchlist Import

批量导入 ticker 到监控池。

主触发词：
- `/dw-import`

兼容别名：
- `/watchlist-import`
- `/import`

只有在当前工作区不存在其他同名系统时，才使用短别名。

## 工作流

1. 解析用户输入，支持逗号、换行、空格分隔。
2. 标准化为大写并去重。
3. 用下面的命令查询公司资料：
   - `python {workspace}/scripts/fetch_market_data.py --profile TICKER1,TICKER2`
4. 按行业和市值分类。
5. 向用户展示拟写入的 watchlist，等待确认。
6. 确认后写入：
   - `config/daily-watchlist-watchlist.md`

如果工作区仍然使用旧文件 `config/watchlist.md`，可以继续兼容读取，但保存时优先写入 namespaced 文件。
