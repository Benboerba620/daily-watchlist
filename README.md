# Daily Watchlist

[![Release](https://img.shields.io/github/v/release/Benboerba620/daily-watchlist?sort=semver)](https://github.com/Benboerba620/daily-watchlist/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> AI stock watchlist, portfolio monitoring, earnings tracking, and daily market report workflow for Claude Code.  
> 面向 Claude Code 的 AI 股票池监控、异动跟踪、财报日历与每日研究日报工作流。

[Latest Release](https://github.com/Benboerba620/daily-watchlist/releases/tag/v1.0.0) | [All Releases](https://github.com/Benboerba620/daily-watchlist/releases) | [Changelog](./CHANGELOG.md)
[中文](#中文) | [English](#english)

# 中文

> AI 驱动的每日股票池监控系统，也是一个给 Claude Code 用的投资研究工作流。维护一个股票池，每天说一句 `/dw-today`，Claude Code 自动拉取行情、检测异动、搜索新闻，生成结构化日报。
>
> **状态**：MVP v1.0.0。你负责维护股票池和关注方向；Claude 负责拉数据、搜新闻、写日报。
> **版本**：[v1.0.0 Release](https://github.com/Benboerba620/daily-watchlist/releases/tag/v1.0.0) | [更新日志](./CHANGELOG.md)

**关键词**：AI 股票池、股票监控、投资研究工作流、每日复盘、异动监控、财报日历、portfolio monitoring、stock watchlist、earnings tracker、Claude Code

## 适合谁？

- 想做一个 **AI stock watchlist / 股票池监控** 系统，但不想自己写完整后端
- 想把 **每日看盘、异动跟踪、财报检查、行业新闻整理** 串成一个固定流程
- 想在 **Claude Code** 里直接运行一个面向投资研究的日报工具
- 已经在用 [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)，想把监控结果继续归档进知识库

**直接按你的情况选一条路：**

| 你是谁 | 走哪条路 |
|---|---|
| 🪟 **Windows 用户 + 编程小白** | [一键安装（PowerShell）](#-windows-小白一键安装推荐) |
| 🍎 **macOS / Linux 用户 + 编程小白** | [一键安装（bash）](#-macos--linux-小白一键安装) |
| 🧑‍💻 **会用 Git / 命令行** | [手动安装](#手动安装) |
| 🤖 **想让 AI agent 帮你装** | 把 [`INSTALL-FOR-AI.md`](./INSTALL-FOR-AI.md) 的链接发给 Claude Code，说"帮我装这个" |

## 最近更新

- `v1.0.1`（2026-04-11）：简化安装后 `CLAUDE.md` 注入、修复 Windows 安装器退出码、新增跨平台 CI 和离线 smoke 测试
- `v1.0.0`（2026-04-10）：首次发布——`/dw-today` 日报 + `/dw-import` 股票池导入 + 模板驱动 + 双平台安装器
- 完整历史见 [`CHANGELOG.md`](./CHANGELOG.md)

---

## 这是什么？

一个在 Claude Code 中运行的 **daily stock watchlist monitor / 每日股票池监控工具**。你维护一个股票池，每天说一句 `/dw-today`，它就会：

1. 拉取你股票池里所有股票的最新行情
2. 检测异动（大盘股 ±3%，小盘股 ±7%，阈值可配）
3. 对异动股搜索新闻，分析原因
4. 检查本周财报日历
5. 按你关注的投资方向搜索行业新闻
6. 生成一份结构化的 markdown 日报
7. （可选）自动归档到 [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)

```mermaid
flowchart TB
    subgraph 配置层
        ENV[".env<br/>API Keys"]
        YAML["config.yaml<br/>模块开关 / 阈值 / 关注方向"]
        WL["watchlist.md<br/>股票池"]
        TPL["report-template.md<br/>日报模板"]
    end

    subgraph 数据层["数据层（Python 脚本，输出 JSON）"]
        FETCH["fetch_market_data.py<br/>行情 + 异动检测 + 财报日历"]
        MACRO["fetch_macro_data.py<br/>VIX / SPY / 黄金 / 原油 / BTC"]
    end

    subgraph 生成层
        GEN["generate_daily_report.py<br/>读取模板 + JSON → 日报骨架"]
    end

    subgraph Claude 层["Claude Code 层"]
        NEWS["WebSearch<br/>异动新闻 + 财报反应 + 主题新闻"]
        VERIFY{"二次验证<br/>（domestic 模式）"}
        FINAL["完成日报<br/>替换占位 → 写入 .md"]
    end

    subgraph 输出
        REPORT["daily-watchlist-reports/<br/>YYYY-MM/YYYY-MM-DD.md"]
        WIKI["wiki/entities/TICKER/news.md<br/>（可选归档）"]
    end

    ENV --> FETCH & MACRO
    YAML --> FETCH & MACRO & GEN
    WL --> FETCH
    TPL --> GEN

    FETCH -- JSON --> GEN
    MACRO -- JSON --> GEN

    GEN -- 骨架 .md --> FINAL
    YAML -. focus_areas .-> NEWS
    NEWS --> VERIFY
    VERIFY -- 通过 --> FINAL
    VERIFY -- 未通过 --> FINAL

    FINAL --> REPORT
    FINAL -. 高信号事件 .-> WIKI
```

> **两阶段分工**：Python 脚本负责拉数据 + 渲染骨架（快、省 token）；Claude 负责新闻搜索 + 验证 + 补充分析（需要判断力的部分）。

---

## 开始之前

你需要准备一个 **FMP API Key**（免费）：

1. 前往 [financialmodelingprep.com](https://site.financialmodelingprep.com/register) 注册
2. 在 Dashboard 复制你的 API Key
3. 免费层每天 250 次请求，个人使用完全够

如果你关注 **A 股或港股**，还需要一个 Tushare token（可选）：
- 前往 [tushare.pro](https://tushare.pro/register) 注册，获取 token

---

## 🪟 Windows 小白：一键安装（推荐）

如果你 **第一次接触这类项目** + **不会 Git / 命令行**，按这 5 步来。

**开始前你只需要知道**：
- 你**不需要**懂编程
- 你**不需要**会 Markdown
- 你的工作是"维护股票池 + 每天说 `/dw-today`"
- 推荐环境：**Windows + Claude Code**

### 1. 安装前置工具

- **Python 3.10+**：前往 [python.org](https://www.python.org/downloads/) 下载安装（勾选 "Add to PATH"）
- **Claude Code**：前往 [claude.ai/claude-code](https://claude.ai/claude-code) 安装
- **Git**（可选）：有就用 git clone，没有就下载 ZIP

### 2. 下载这个项目

二选一：
- 会用 git：打开终端，运行 `git clone https://github.com/Benboerba620/daily-watchlist.git`
- 不会用 git：在 GitHub 页面点 **Code → Download ZIP**，解压

### 3. 一键安装到你的项目目录

打开 PowerShell（Windows 搜索栏搜"PowerShell"），运行：

```powershell
# 如果 PowerShell 提示"无法运行脚本"，先执行这行（只需一次）：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

cd 你下载解压的路径\daily-watchlist
.\scripts\install.ps1 -TargetDir "D:\my-investment"
```

如果安装器最后只提示 `FMP_API_KEY` 未填写，这是正常的首次安装状态，不算安装失败。

这一条命令会自动帮你：
- 复制脚本、模板、Claude skills 到目标目录
- 创建配置文件（你只需要填 API key）
- 创建日报输出目录
- 设置 `CLAUDE.md`（已有文件时只追加轻量入口）

如果你还没有自己的项目目录，把 `-TargetDir` 指到一个全新的空文件夹即可。

### 4. 填入你的 API Key

安装脚本已经自动创建了配置文件，直接编辑即可：

```powershell
notepad "D:\my-investment\config\daily-watchlist.env"
```

在打开的记事本里，把 `your_fmp_api_key_here` 替换成你在第 0 步拿到的 FMP API Key，保存。

### 5. 打开 Claude Code，导入你的股票池

在 Claude Code 中说：

> /dw-import

然后粘贴你的股票列表（逗号分隔就行，200 只以内都没问题）：

> AAPL, MSFT, GOOGL, NVDA, TSLA, AMZN, JPM, XOM, UNH, JNJ

Claude 会自动查询每只股票的信息，按行业分类，让你确认后保存。

然后说：

> /dw-today

你的第一份日报就生成了。

### 小白常见问题

- **不懂 Git，能用吗？** 可以，下载 ZIP 解压也行。
- **免费够用吗？** FMP 免费层 250 次/天，监控 100 只股票 + 宏观数据绰绰有余。
- **只关注 A 股？** 需要额外注册 Tushare（免费），在 `.env` 里填入 `TUSHARE_TOKEN`。
- **只想先试试，不想污染现有项目？** 把 `-TargetDir` 指到一个全新的空文件夹。
- **日报在哪？** `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`。
- **怎么修改关注方向？** 编辑 `config/daily-watchlist.yaml` 里的 `focus_areas`。

---

## 🍎 macOS / Linux 小白：一键安装

和 Windows 版完全等价的 bash 版本。

### 1. 下载

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
```

不会用 git：从 GitHub 页面 **Code → Download ZIP**，解压，`cd` 进去。

### 2. 一键安装

```bash
bash scripts/install.sh --target-dir ~/my-investment
```

如果安装器最后只提示 `FMP_API_KEY` 未填写，这是正常的首次安装状态，不算安装失败。

### 3. 填入 API Key

安装脚本已经自动创建了配置文件，直接编辑即可：

```bash
nano ~/my-investment/config/daily-watchlist.env
```

### 4. 打开 Claude Code

先说 `/dw-import`，粘贴你的股票列表。然后说 `/dw-today` 生成第一份日报。

---

## 手动安装

适合已经会用 git / 命令行的人。

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp

# macOS / Linux
bash ./.daily-watchlist-tmp/scripts/install.sh --target-dir ./daily-watchlist

# Windows PowerShell
.\.daily-watchlist-tmp\scripts\install.ps1 -TargetDir .\daily-watchlist
```

安装后：
1. 编辑 `config/daily-watchlist.env` 填入 FMP API key（安装脚本已自动创建）
2. 按需编辑 `config/daily-watchlist.yaml`（模块开关、异动阈值、关注方向）
3. `python scripts/check_setup.py` 验证环境
4. 在 Claude Code 中说 `/dw-import` 导入股票池，说 `/dw-today` 生成日报

---

## 让 AI agent 帮你装

打开 Claude Code（或 Cursor / Cline 等），发这条消息：

> 帮我装这个：https://github.com/Benboerba620/daily-watchlist/blob/main/INSTALL-FOR-AI.md

Agent 会按安装协议走完全流程：确认市场、填入 key、导入股票池、生成配置、交付。

---

## 功能详情

如果你在搜这些词，这个项目就是对应的实现：

- `AI stock watchlist`
- `stock watchlist for Claude Code`
- `portfolio monitoring workflow`
- `daily stock report generator`
- `earnings tracker with AI`
- `investment research workflow`

### 股票池管理

说 `/dw-import`，粘贴 ticker 列表（支持 200+），Claude 自动：
- 查询公司名、市值、行业
- 按行业分类
- 让你确认后保存到 `config/daily-watchlist-watchlist.md`

### 每日简报

说 `/dw-today`，Claude 自动：
- 拉取全部股票行情 + 宏观指标（VIX / SPY / QQQ / 黄金 / 原油 / BTC）
- 检测异动，搜索新闻分析原因
- 检查本周财报日历
- 按关注方向搜索行业新闻
- 基于报告模板生成结构化日报到 `daily-watchlist-reports/YYYY-MM/`

每个模块（宏观、财报、关注方向）都可以在 `config.yaml` 里独立开关——关掉的模块不拉数据、不占 API 额度。

### 关注方向（Focus Areas）

在 `config/daily-watchlist.yaml` 中定义你关注的投资主题：

```yaml
focus_areas:
  - name: "AI & Data Center"
    keywords: ["AI", "data center", "GPU", "inference"]
    required_any: ["data center", "GPU", "inference"]
    exclude: ["airline", "ceasefire"]
```

Claude 每天按关键词搜索行业新闻，并用 `required_any` 过滤无关结果、用 `exclude` 剔除噪音。

### 自定义日报模板

日报的结构由 `templates/daily-watchlist-report-template.md` 控制。脚本会读取这个模板，用实时数据填充变量后生成骨架，Claude 再补充新闻和分析。

你可以直接编辑模板来调整日报的段落顺序、标题措辞、表格列，改完下次 `/dw-today` 就生效。

### Wiki 归档

如果你的项目已经安装了 [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)，Daily Watchlist 会自动检测 `wiki/entities/`，将重大异动和财报事件归档到对应 entity 的 `news.md`。

### 国产模型二次验证

如果你使用国产模型（如 DeepSeek、Kimi 等），建议在 `config/daily-watchlist.yaml` 中开启：

```yaml
reporting:
  model_profile: domestic
  secondary_verify: true
```

开启后，Claude 在写入日报前会对每条新闻做二次验证：核对来源可信度、发布时间、正文事实一致性。未通过验证的条目标记为"待人工确认"而不是直接写入。

---

## 配置参考

| 文件 | 用途 |
|------|------|
| `config/daily-watchlist.env` | API keys |
| `config/daily-watchlist.yaml` | 模块开关、阈值、关注方向 |
| `config/daily-watchlist-watchlist.md` | 你的股票池 |
| `templates/daily-watchlist-report-template.md` | 日报模板（可自行编辑） |

### 触发词

| 推荐 | 兼容别名 |
|------|----------|
| `/dw-today` | `/watchlist-today`（仅兼容） |
| `/dw-import` | `/watchlist-import`（仅兼容） |

优先使用 `/dw-today` 和 `/dw-import`。在共享工作区里，不要默认依赖 `/today` 和 `/import` 这类高冲突短别名。

只有在当前工作区没有冲突时，才建议使用短别名。

### 必需的 API Key

| 服务 | 用途 | 费用 |
|------|------|------|
| [FMP](https://site.financialmodelingprep.com/register) | 美/欧/日股行情 + 财报（必需） | 免费（250 次/天） |
| [Tushare](https://tushare.pro/register) | A 股 / 港股行情（可选） | 免费 |

---

## 致谢

- [Claude Code](https://claude.ai/claude-code) — 运行环境
- [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) — 知识归档系统

## 关于作者

更多投资思考、研究方法与系统化协作的文章，欢迎关注微信公众号 **奔波儿r**。

## 协议

MIT

---

# English

> An AI-powered daily stock monitoring system and investing workflow for Claude Code. Maintain a watchlist, say `/dw-today`, and Claude Code automatically fetches prices, detects movers, searches for news, and generates a structured daily report.
>
> **Status**: MVP v1.0.0. You maintain the watchlist and focus areas; Claude handles data, news, and reports.
> **Release**: [v1.0.0](https://github.com/Benboerba620/daily-watchlist/releases/tag/v1.0.0) | [Changelog](./CHANGELOG.md)

**Keywords**: AI stock watchlist, portfolio monitoring, stock mover detection, earnings tracker, daily stock report, investing workflow, Claude Code, watchlist automation

## Who Is This For?

- You want an **AI stock watchlist** without building a full investing dashboard from scratch
- You want one repeatable workflow for **price checks, mover detection, earnings tracking, and daily research notes**
- You use **Claude Code** and want a practical investing / market monitoring tool inside it
- You already use [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) and want market updates archived into your research system

**Pick the path that matches you:**

| Who you are | Where to go |
|---|---|
| 🪟 **Windows + coding beginner** | [One-shot install (PowerShell)](#-windows-beginner-one-shot-install-recommended) |
| 🍎 **macOS / Linux + coding beginner** | [One-shot install (bash)](#-macos--linux-beginner-one-shot-install) |
| 🧑‍💻 **Comfortable with git / CLI** | [Manual install](#manual-install) |
| 🤖 **Want an AI agent to install it** | Send [`INSTALL-FOR-AI.md`](./INSTALL-FOR-AI.md) to Claude Code and say "install this for me" |

## Recent Updates

- `v1.0.1` (2026-04-11): Streamlined installed `CLAUDE.md` hint; fixed Windows installer exit code; added cross-platform CI and offline smoke tests
- `v1.0.0` (2026-04-10): First release — `/dw-today` daily report + `/dw-import` watchlist import + template-driven generation + dual-platform installers
- Full history: [`CHANGELOG.md`](./CHANGELOG.md)

---

## What is this?

A **daily stock watchlist monitor** that runs inside Claude Code. Maintain a watchlist, say `/dw-today`, and it will:

1. Fetch latest prices for all stocks in your watchlist
2. Detect significant movers (large-cap ±3%, small-cap ±7%, configurable)
3. Search news for movers and analyze causes
4. Check this week's earnings calendar
5. Search industry news based on your focus areas
6. Generate a structured markdown report
7. (Optional) Auto-archive to [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)

```mermaid
flowchart TB
    subgraph Config
        ENV[".env<br/>API Keys"]
        YAML["config.yaml<br/>Modules / Thresholds / Focus Areas"]
        WL["watchlist.md<br/>Stock Pool"]
        TPL["report-template.md<br/>Report Template"]
    end

    subgraph Data["Data Layer (Python scripts, JSON output)"]
        FETCH["fetch_market_data.py<br/>Quotes + Mover Detection + Earnings"]
        MACRO["fetch_macro_data.py<br/>VIX / SPY / Gold / Oil / BTC"]
    end

    subgraph Generation
        GEN["generate_daily_report.py<br/>Template + JSON → Report Skeleton"]
    end

    subgraph Claude["Claude Code Layer"]
        NEWS["WebSearch<br/>Mover News + Earnings + Themes"]
        VERIFY{"Secondary Verify<br/>(domestic mode)"}
        FINAL["Finalize Report<br/>Fill placeholders → Write .md"]
    end

    subgraph Output
        REPORT["daily-watchlist-reports/<br/>YYYY-MM/YYYY-MM-DD.md"]
        WIKI["wiki/entities/TICKER/news.md<br/>(optional archive)"]
    end

    ENV --> FETCH & MACRO
    YAML --> FETCH & MACRO & GEN
    WL --> FETCH
    TPL --> GEN

    FETCH -- JSON --> GEN
    MACRO -- JSON --> GEN

    GEN -- skeleton .md --> FINAL
    YAML -. focus_areas .-> NEWS
    NEWS --> VERIFY
    VERIFY -- pass --> FINAL
    VERIFY -- fail --> FINAL

    FINAL --> REPORT
    FINAL -. high-signal events .-> WIKI
```

> **Two-phase design**: Python scripts handle data fetching + skeleton rendering (fast, token-efficient); Claude handles news search + verification + analysis (the parts requiring judgment).

---

## Before You Start

You need a **FMP API Key** (free):

1. Go to [financialmodelingprep.com](https://site.financialmodelingprep.com/register) and register
2. Copy your API Key from the Dashboard
3. Free tier: 250 requests/day, more than enough for personal use

For **A-shares or HK stocks**, also get a Tushare token (optional):
- Register at [tushare.pro](https://tushare.pro/register)

---

## 🪟 Windows beginner: one-shot install (recommended)

If you're **new to projects like this** + **don't know git / CLI**, follow these 5 steps.

**Before you start, you only need to know**:
- You **don't** need to know programming
- You **don't** need to know Markdown
- Your job is: "maintain a stock list + say `/dw-today` every day"
- Recommended: **Windows + Claude Code**

### 1. Install prerequisites

- **Python 3.10+**: download from [python.org](https://www.python.org/downloads/) (check "Add to PATH")
- **Claude Code**: install from [claude.ai/claude-code](https://claude.ai/claude-code)
- **Git** (optional): if you have it, use `git clone`; otherwise download ZIP

### 2. Download this project

Either:
- With git: `git clone https://github.com/Benboerba620/daily-watchlist.git`
- Without git: on GitHub, click **Code → Download ZIP**, then unzip

### 3. One-shot install

Open PowerShell (search "PowerShell" in Windows), run:

```powershell
# If PowerShell says "cannot run scripts", run this first (one-time only):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

cd path\to\daily-watchlist
.\scripts\install.ps1 -TargetDir "D:\my-investment"
```

This copies scripts, templates, Claude skills, creates config files, and sets up the report directory.

### 4. Add your API Key

The install script already created the config file. Just edit it:

```powershell
notepad "D:\my-investment\config\daily-watchlist.env"
```

Replace `your_fmp_api_key_here` with your FMP API Key, save.

### 5. Open Claude Code and start

Say `/dw-import`, then paste your stock list:

> AAPL, MSFT, GOOGL, NVDA, TSLA, AMZN, JPM, XOM, UNH, JNJ

Claude auto-classifies them by sector. Confirm, then say `/dw-today` for your first report.

### Beginner FAQ

- **No git?** Download ZIP works fine.
- **Is the free tier enough?** Yes. 250 req/day covers 100+ stocks + macro.
- **Only follow A-shares?** Register Tushare (free), add `TUSHARE_TOKEN` to `.env`.
- **Just want to try without affecting existing files?** Point `-TargetDir` at a new empty folder.
- **Where are my reports?** `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`
- **How to change focus areas?** Edit `focus_areas` in `config/daily-watchlist.yaml`.

---

## 🍎 macOS / Linux beginner: one-shot install

Behaviour-equivalent bash version.

### 1. Download

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
```

### 2. Install

```bash
bash scripts/install.sh --target-dir ~/my-investment
```

### 3. Add API Key

The install script already created the config file. Just edit it:

```bash
nano ~/my-investment/config/daily-watchlist.env
```

### 4. Open Claude Code

Say `/dw-import`, paste your tickers. Then `/dw-today` for your first report.

---

## Manual install

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp

# macOS / Linux
bash ./.daily-watchlist-tmp/scripts/install.sh --target-dir ./daily-watchlist

# Windows PowerShell
.\.daily-watchlist-tmp\scripts\install.ps1 -TargetDir .\daily-watchlist
```

Then: edit `config/daily-watchlist.env` to add your API key (auto-created by installer), review `config/daily-watchlist.yaml`, run `python scripts/check_setup.py`, then use `/dw-import` and `/dw-today`. Prefer the `/dw-*` commands in shared workspaces.

---

## Let an AI agent install it

Open Claude Code (or Cursor / Cline) and say:

> Install this for me: https://github.com/Benboerba620/daily-watchlist/blob/main/INSTALL-FOR-AI.md

---

## Features

If you found this repo by searching for one of these terms, you're in the right place:

- `AI stock watchlist`
- `daily stock monitoring`
- `portfolio monitoring with AI`
- `Claude Code investing workflow`
- `earnings tracker`
- `daily market report generator`

- **Watchlist import**: paste 200+ tickers, auto-classified by sector
- **Mover detection**: configurable thresholds, auto news search
- **Macro dashboard**: VIX, SPY, QQQ, gold, oil, BTC
- **Earnings calendar**: auto-track for watched stocks
- **Focus areas**: custom keywords for daily industry news
- **Customizable template**: edit the report template to change structure, headers, or columns
- **Module toggles**: turn off macro/earnings/focus_areas individually — disabled modules skip data fetching entirely
- **Wiki archiving**: auto-integrates with karpathy-claude-wiki
- **Secondary verification**: for domestic model users, news verified before inclusion

## API Keys

| Service | Purpose | Cost |
|---------|---------|------|
| [FMP](https://site.financialmodelingprep.com/register) | US/EU/JP quotes + earnings (required) | Free (250 req/day) |
| [Tushare](https://tushare.pro/register) | A-shares / HK quotes (optional) | Free |

## Triggers

| Recommended | Aliases |
|-------------|---------|
| `/dw-today` | `/watchlist-today` (compatibility only) |
| `/dw-import` | `/watchlist-import` (compatibility only) |

Prefer `/dw-today` and `/dw-import`. Avoid relying on `/today` and `/import` in shared workspaces because those short aliases are more likely to conflict with other systems.

## Credits

- [Claude Code](https://claude.ai/claude-code)
- [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)

## License

MIT
