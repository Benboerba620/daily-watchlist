# 更新日志

这里记录 `daily-watchlist` 的重要更新。版本号使用语义化版本（SemVer），发布在 [GitHub Releases](https://github.com/Benboerba620/daily-watchlist/releases)。

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
