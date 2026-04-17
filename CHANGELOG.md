# 更新日志

这里记录 `daily-watchlist` 的重要更新。版本号使用语义化版本（SemVer），发布在 [GitHub Releases](https://github.com/Benboerba620/daily-watchlist/releases)。

## [1.0.3] - 2026-04-17

### 文档

- **README 结构重排**：把 🤖 AI agent 安装升为首推路径，PowerShell/bash 一键脚本和手动安装都折叠进 `<details>` 块；路由表从 4 行改为 3 行（AI agent → 本地脚本 → 手动）
- 之所以这样改：对真小白来说，"打开终端 + 翻文档找命令 + 复制粘贴 + 改路径参数"的门槛比"给 Claude Code 发一句 URL"高得多；AI agent 路径又是近乎零操作
- 「让 AI agent 帮你装」章节扩写为 3 步流程 + 明确列出 agent 会问的 7 个澄清问题，小白能提前预期
- 新增 Beginner FAQ 补 Cursor / Cline / Windsurf 的替代选项链接，避免"没有 Claude Code 就用不了"的错觉
- 中英双语同步

### 修复

- `install.ps1` / `install.sh`：`TargetDir` 是 cwd 子目录时，自动在项目根 `CLAUDE.md` 追加 Daily Watchlist 路由段（指回 workspace 级 CLAUDE.md 和 skills）。`INSTALL-FOR-AI.md` Phase 4 原本就要求「与现有根 CLAUDE.md 融合」，之前实装只写 workspace 级，没触根。幂等（已存在不重复追加）
- `scripts/fetch_market_data.py` `--profile` 模式：`.SH` / `.SZ` / `.HK` 后缀的 ticker 强制走 Tushare 而不是 FMP。FMP 对 A 股覆盖不全（比如 `601857.SH` 中国石油拿不到），Tushare 是 A 股 / 港股的权威源，即便 FMP 某个 ticker 碰巧有数据也应优先用 Tushare
- `scripts/fetch_market_data.py` `classify_market_cap`：根据 country 自动换算市值阈值（CN / HK ≈ 7× USD 阈值），避免人民币市值被 USD 阈值误判
- `scripts/generate_daily_report.py` `render_other_movers`：去掉已经在「重点异动」表里的 ticker，避免 NVDA 这样的大异动在两个表里重复出现

### 改进

- `scripts/fetch_market_data.py`：`ENABLE_YFINANCE=1` 但 `yfinance` 没装时，warning 改为线程安全的一次性提示，不再每只股票重复输出
- `.github/workflows/install-test.yml`：CI 新增「Run fallback unit tests」步骤
- `tests/test_fetch_market_data.py`：新增 fallback 链路的单元测试覆盖
- `.gitignore`：忽略百度同步盘冲突副本 `*_冲突文件_*`

## [1.0.2] - 2026-04-16

### 新增

- FMP 没返回某 ticker 时，脚本自动按备选链兜底：Stooq（零配置，US/JP/DE）→ Finnhub（填 `FINNHUB_API_KEY` 启用，美股）→ EOD（填 `EOD_API_KEY` 启用，港/韩/芬兰）→ yfinance（`ENABLE_YFINANCE=1` 且装好包才启用）
- README 新增"数据源"小节（中英双版），列出所有实际踩过的备选 API + 状态列 + 各自的坑
- `config/daily-watchlist.env.example` 增加可选 key 占位：`FINNHUB_API_KEY`、`EOD_API_KEY`、`ENABLE_YFINANCE`

### 说明

- Stooq 用的是 `/q/l/` 实时端点（无需 apikey），不是 `/q/d/l/` 历史端点（2026 起需要 apikey）
- yfinance 在国内访问不稳定，因此默认关闭，通过 `ENABLE_YFINANCE=1` 显式开启

## [1.0.1] - 2026-04-11

### 改进

- 简化安装后注入的 `CLAUDE.md` 提示，让目标工作区保持轻量入口，不再堆积协议文本
- 统一文档和安装器中的命令推荐：共享工作区优先使用 `/dw-today` 和 `/dw-import`
- 首次安装时 `FMP_API_KEY` 未填写现在显示为"正常的首次安装状态"，而非安装失败

### 修复

- 修复 Windows 安装器退出码：CI 和首次安装不再因 API key 未填写而报错
- 统一环境检查和文档中的 Python 版本要求为 3.10+
- 移除安装器中对复制 `.example` 文件的过时引用

### 新增

- 新增跨平台安装测试 CI：覆盖 Windows / macOS / Ubuntu，Python 3.10、3.11、3.12
- 新增离线 smoke-report 生成器：验证新安装的工作区能否在无 API 调用的情况下渲染日报骨架
- 新增 CI 断言：确保安装后的 `CLAUDE.md` 保持轻量、日报模板无未解析占位符

## [1.0.0] - 2026-04-10

Daily Watchlist 首次公开发布。

### 新增

- Claude Code 工作流：`/dw-today`（生成日报）和 `/dw-import`（导入股票池）
- 模板驱动的日报生成，支持模块级开关（宏观 / 财报 / 关注方向可独立关闭）
- 股票行情和宏观数据拉取脚本，支持 FMP + Tushare 双数据源
- Windows PowerShell 和 Unix bash 一键安装脚本
- 面向小白的中英双语 README 和 AI agent 安装协议
