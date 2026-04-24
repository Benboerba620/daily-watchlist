# Daily Watchlist Today

生成每日监控简报。

主触发词：
- `/dw-today`

兼容别名：
- `/watchlist-today`
- `/today`

只有在当前工作区不存在其他同名系统时，才使用短别名。

## 工作流

### Step 1: 读取配置

一次性读取以下文件：
- `config/daily-watchlist.yaml` → 解析 modules、thresholds、focus_areas、**reporting** 配置
- `config/daily-watchlist-watchlist.md`
  - Required columns: `Ticker`, `Name`, `Market`, `Market Cap`, `Category`
  - Optional columns: `Tier`, `Hypothesis`, `Notes` for read-only hypothesis-linked monitoring
  - Do not read or write portfolio/holdings files in Daily Watchlist
- `templates/daily-watchlist-report-template.md`

**关键检查**：读取 `reporting` 段，记住以下两个值（后续步骤依赖）：
- `reporting.model_profile` — 如果是 `domestic`，启用二次验证
- `reporting.secondary_verify` — 如果是 `true`，启用二次验证

只要其中任一条件满足，本次运行的所有 WebSearch 结果都必须走二次验证流程（见下方"二次验证协议"）。

### Step 2: 生成数据骨架

运行脚本（并行）：
```bash
python {workspace}/scripts/generate_daily_report.py
```

该脚本会：
1. 调用 `fetch_market_data.py` + `fetch_macro_data.py`
2. 生成骨架报告到 `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`
3. 骨架中的"待补充"占位文字需要在后续步骤中替换

读取生成的骨架报告。

### Step 3: 新闻搜索

新闻检索必须由 Claude Code 通过 WebSearch 完成，不要用本地脚本替代。

**异动新闻**：对骨架中"重点异动"表格里的每只股票：
- WebSearch: `"{ticker} {name} stock news today"`
- 提取原因、因果链

**财报反应**：对"已披露"表格中有实际 EPS 的股票：
- WebSearch: `"{ticker} earnings reaction"`

**主题新闻**：对 config 中的每个 focus_area（最多 3 个）：
- 用 `keywords` 构造搜索词
- 如果 focus_area 定义了 `required_any`：搜索结果必须包含至少一个 required_any 关键词才纳入
- 如果 focus_area 定义了 `exclude`：搜索结果标题/摘要包含 exclude 关键词的直接丢弃

### Step 4: 二次验证协议

**触发条件**：`reporting.model_profile == "domestic"` 或 `reporting.secondary_verify == true`

如果**未触发**：跳过本步骤，直接进入 Step 5。

如果**触发**：对 Step 3 中准备写入报告的每一条新闻，执行以下验证：

1. **来源可信度**：来源域名/媒体是否为已知财经媒体？个人博客、论坛帖子降级处理
2. **时效性**：发布时间是否在今日或昨日？URL 不含日期的，必须点开确认
3. **事实一致性**：标题中的关键事实（数字、公司名、事件）是否和正文一致？
4. **可核对性**：报告中即将写入的数字、日期、公司名，是否能在原文中找到？

**验证结果处理**：
- 全部通过 → 写入报告
- 部分通过但关键事实可核对 → 写入，但标注来源存疑点
- 未通过 → **不写结论**，改为标记 `⚠️ 待人工确认：{原因}`
- 只有单一来源且事实密度高 → 尝试补第二来源，否则降级为"待人工确认"

**写作约束**（二次验证模式下）：
- 优先写可核对事实 + 来源链接
- 少写高自由度概括和推测
- 不要为了"填满"报告而降低验证标准

### Step 5: 完成报告

读取 Step 2 生成的骨架报告，用 Step 3/4 的结果替换所有占位文字：
- "用 WebSearch 补新闻与原因分析" → 替换为实际新闻摘要和因果链
- "用 Claude Code WebSearch 进行主题新闻检索" → 替换为实际主题新闻
- "当前没有财报条目" → 如果搜索到了财报信息则替换
- 删除所有剩余的"待补充"占位文字

用 Edit 工具将最终内容写入 `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`。

### Step 6: Wiki 归档（如有）

检查 `wiki/entities/` 是否存在。如果存在，只归档高信号事件：
- 涨跌幅 ≥10% 的异动
- 财报 beat/miss 结果

格式：追加到 `wiki/entities/{TICKER}/news.md`
```markdown
## YYYY-MM-DD
- {TICKER} {+/-X.X%}: {一句话原因} ([source](url))
```

## 失败处理

- 脚本失败时跳过对应部分，继续后续流程
- WebSearch 失败时标记为"待人工补充"
- 不要编造数据
