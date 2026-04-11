# Daily Watchlist Protocols

这是 Daily Watchlist 系统的源协议文件。新版安装器不会再把它整份复制到目标工作区，而是只向目标 `CLAUDE.md` 注入一个轻量入口段。

## 目标

Daily Watchlist 是一个由 Claude 驱动的市场监控工作流，用来：

- 读取监控池
- 拉取行情、异动、财报和宏观数据
- 研究重点异动和关注主题
- 生成结构化中文日报

## 主触发词

- `/dw-today`
- `/dw-import`

## 兼容别名

- `/watchlist-today`
- `/watchlist-import`
- `/today`
- `/import`

只有在当前工作区没有其他系统占用这些短命令时，才使用别名。

## 规范路径

- `config/daily-watchlist.env`
- `config/daily-watchlist.yaml`
- `config/daily-watchlist-watchlist.md`
- `templates/daily-watchlist-report-template.md`
- `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`

Python 脚本仍兼容旧路径：

- `config/.env`
- `config/config.yaml`
- `config/watchlist.md`
- `templates/report-template.md`

## 协议：日报生成

1. 读取：
   - `config/daily-watchlist.yaml`
   - `config/daily-watchlist-watchlist.md`
   - `templates/daily-watchlist-report-template.md`

2. 并行运行：
   - `python scripts/fetch_market_data.py`
   - 如果开启宏观模块，再运行 `python scripts/fetch_macro_data.py`

3. 新闻检索只覆盖：
   - 超过阈值的个股异动
   - 重要财报更新
   - 最多 3 个 focus areas

4. 优先使用 `python scripts/generate_daily_report.py` 直接生成日报。
   - 默认按模板结构输出
   - 默认使用中文撰写
   - 明确告诉用户模板是可编辑的
   - 新闻部分由 Claude Code 通过 WebSearch 补充，而不是由本地新闻接口替代

5. 将最终报告保存到：
   - `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`

6. 如果存在 `wiki/entities/`，只归档高信号事件。

## 协议：监控池导入

1. 从用户输入中解析 ticker。
2. 标准化并去重。
3. 用 `fetch_market_data.py --profile` 查询基础资料。
4. 按行业和市值分类。
5. 让用户确认。
6. 保存到 `config/daily-watchlist-watchlist.md`。

## 写作规则

- 数据驱动，数字明确
- 必要结论附 URL 来源
- 不编造缺失信息
- 某个部分失败时，明确说明并继续其他部分
- 如果 `reporting.model_profile: domestic` 或 `reporting.secondary_verify: true`，主题新闻必须经过更严格的二重筛选后才能写入报告

## WebSearch 二次验证规则

当 `reporting.model_profile: domestic` 或 `reporting.secondary_verify: true` 时：

1. 第一轮 WebSearch 只做候选召回
2. 第二轮必须逐条核对候选新闻再落笔
3. 至少核对以下内容：
   - 来源域名/媒体是否可信
   - 发布时间是否与“今日/本周”表述一致
   - 标题和正文是否一致
   - 写入日报的数字、日期、公司名是否能在原文中找到
4. 如果某条新闻只能找到单一来源，且事实密度高：
   - 尽量补第二来源
   - 否则降级为“待人工确认”
5. 对国产模型场景，优先写“可核对事实 + 来源”，少写高自由度概括
