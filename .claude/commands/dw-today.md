---
description: 生成 Daily Watchlist 今日简报
---

生成每日监控简报。

## 工作流

### Step 1: 读取配置

一次性读取以下文件：
- `config/daily-watchlist.yaml`
- `config/daily-watchlist-watchlist.md`
- `templates/daily-watchlist-report-template.md`
- `config/hypothesis-tracker.yaml`（如存在）
- `hypothesis/H*.md`（如存在）

重点读取 `reporting` 段：
- `reporting.model_profile`
- `reporting.secondary_verify`

只要 `reporting.model_profile == "domestic"` 或 `reporting.secondary_verify == true`，后续所有 WebSearch 结果都必须执行二次验证。

### Step 2: 先触发日报生成脚本

必须先执行：

```bash
python scripts/generate_daily_report.py
```

执行后会在 `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md` 生成一份日报骨架。读取该文件，后续所有补充都基于这份新生成的日报进行。
如果存在 `hypothesis/H*.md`，脚本会同时生成“假设联动”区，并把本地可确认的异动/财报信号回写为证据。

### Step 3: 补新闻与主题

新闻检索必须由 Claude Code 通过 WebSearch 完成。

异动新闻：
- 对“重点异动”中的每只股票搜索 `"{ticker} {name} stock news today"`

财报反应：
- 对“已披露”中存在实际 EPS 的股票搜索 `"{ticker} earnings reaction"`

主题新闻：
- 对配置中的每个 `focus_area`（最多 3 个）按 `keywords` 组合搜索
- 命中 `required_any` 才纳入
- 命中 `exclude` 直接剔除

### Step 4: 二次验证

触发二次验证时，逐条检查：
1. 来源是否可信
2. 发布时间是否足够新
3. 标题与正文关键事实是否一致
4. 报告中引用的数字、日期、公司名能否在原文核对

处理规则：
- 可核对且可信：写入日报
- 关键信息可核对但来源一般：写入并标注疑点
- 无法核对：写成 `⚠️ 待人工确认：{原因}`

### Step 5: 完成日报

把骨架里的占位内容替换为实际内容：
- “用 WebSearch 补充新闻与原因分析”
- “用 Claude Code WebSearch 进行主题新闻检索并在核实来源后写入”
- 其他占位说明

最终写回 `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`。

### Step 6: Wiki 归档（如有）

如果存在 `wiki/entities/`，仅归档高信号事件：
- 涨跌幅绝对值大于等于 10%
- 财报 beat/miss

格式：

```markdown
## YYYY-MM-DD
- {TICKER} {+/-X.X%}: {一句话原因} ([source](url))
```

## 失败处理

- 脚本失败时跳过对应部分，继续后续流程
- WebSearch 失败时标记为“待人工补充”
- 不要编造数据
