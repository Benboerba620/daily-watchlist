# Daily Watchlist

[![Release](https://img.shields.io/github/v/release/Benboerba620/daily-watchlist?sort=semver)](https://github.com/Benboerba620/daily-watchlist/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> 🔗 **"零代码 AI 投研三件套" 之一** ｜ Part of the zero-code AI investment research toolkit
> [知识库底座 karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) · 日常盯盘 daily-watchlist · [假设追踪 hypothesis-tracker](https://github.com/Benboerba620/hypothesis-tracker)

> AI stock watchlist, portfolio monitoring, earnings tracking, and daily market report workflow for Claude Code.
> 面向 Claude Code 的 AI 股票池监控、异动跟踪、财报日历与每日研究日报工作流。

[Latest Release](https://github.com/Benboerba620/daily-watchlist/releases) | [All Releases](https://github.com/Benboerba620/daily-watchlist/releases) | [Changelog](./CHANGELOG.md)
[中文](#中文) | [English](#english)

# 中文

> AI 驱动的每日股票池监控系统，也是一个给 Claude Code 用的投资研究工作流。维护一个股票池，每天说一句 `/dw-today`，Claude Code 自动拉取行情、检测异动、搜索新闻，生成结构化日报。
>
> **状态**：MVP。你负责维护股票池和关注方向；Claude 负责拉数据、搜新闻、写日报。
> **版本**：[最新 Release](https://github.com/Benboerba620/daily-watchlist/releases) | [更新日志](./CHANGELOG.md)

**关键词**：AI 股票池、股票监控、投资研究工作流、每日复盘、异动监控、财报日历、portfolio monitoring、stock watchlist、earnings tracker、Claude Code

## 适合谁？

- 想做一个 **AI stock watchlist / 股票池监控** 系统，但不想自己写完整后端
- 想把 **每日看盘、异动跟踪、财报检查、行业新闻整理** 串成一个固定流程
- 想在 **Claude Code** 里直接运行一个面向投资研究的日报工具
- 已经在用 [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki)，想把监控结果继续归档进知识库

**直接按你的情况选一条路：**

| 你是谁 | 走哪条路 |
|---|---|
| 🤖 **让 AI agent 帮你装（推荐）** | [让 Claude Code / AI agent 帮你装](#-推荐让-claude-code--ai-agent-帮你装) |
| 🧑‍💻 **会用命令行想自己装** | [进阶：本地脚本安装](#进阶本地脚本安装-windows--macos--linux) |
| 🛠️ **想完全手动一步步来** | [进阶：手动安装](#进阶手动安装-5-分钟) |

## 最近更新

- `2026-04-17`：README 结构重排（AI agent 安装升为首推），install 脚本现在会给根 CLAUDE.md 追加路由段，`--profile` 模式下 A 股/港股强制走 Tushare（FMP 对 `.SH/.SZ` 覆盖不全），smoke 报告去重
- `v1.0.2`（2026-04-16）：新增 Stooq / Finnhub / EOD / yfinance 行情兜底链，README 增加数据源说明，`env.example` 增加可选配置
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

```
watchlist.md ──→ fetch_market_data.py ──→ JSON ──┐
                                                  │
config.yaml ───→ fetch_macro_data.py ───→ JSON ──┤
                                                  ├──→ generate_daily_report.py
                 FMP earnings calendar ──→ JSON ──┤        │
                                                  │        ├──→ 日报骨架 .md
report-template.md ───────────────────────────────┘        │
                                                           ↓
focus_areas ───→ Claude WebSearch ──────────────→ Claude 补充新闻
                                                           │
                                                  wiki/ ←──┘ (归档)
```

---

## 开始之前

你需要准备一个 **FMP API Key**（免费）：

1. 前往 [financialmodelingprep.com](https://site.financialmodelingprep.com/register) 注册
2. 在 Dashboard 复制你的 API Key
3. 免费层每天 250 次请求，个人使用完全够

如果你关注 **A 股或港股**，还需要一个 Tushare token（推荐，A 股走 FMP 覆盖不全）：
- 前往 [tushare.pro](https://tushare.pro/register) 注册，获取 token

> 💡 **FMP 250/天不够用、或某只股票 FMP 没数据？** 脚本内置了自动兜底链：**Stooq**（零配置，美/日/德）、**Finnhub**（填 key 即启用，美股）、**EOD**（填 key 即启用，港/韩/芬兰）、**yfinance**（可选开关，国内慎用）。每个源的覆盖范围、免费额度、踩过的坑见下面 [数据源](#数据源) 章节。

---

## 🤖 推荐：让 Claude Code / AI agent 帮你装

**为什么推荐这条路**：对真小白来说，"打开终端 + 翻文档找命令 + 复制粘贴 + 改路径参数"的门槛比"给 Claude Code 发一句话"高得多。AI agent 路径几乎零操作。

**前置**（各 1-3 分钟）：
1. 装好 [Claude Code](https://claude.ai/claude-code)（Cursor / Cline / Windsurf 也行，只要支持 Agent 模式）
2. 拿到 [FMP API Key](https://site.financialmodelingprep.com/register)（免费，注册 1 分钟）
3. 关心 A 股/港股的话，顺手拿个 [Tushare token](https://tushare.pro/register)

**3 步就好**：

1. 在 Claude Code 里打开你想安装的项目目录（或一个全新空文件夹）
2. 给 agent 发：

   > 帮我装这个：https://github.com/Benboerba620/daily-watchlist/blob/main/INSTALL-FOR-AI.md

3. agent 会按 [INSTALL-FOR-AI.md](./INSTALL-FOR-AI.md) 协议问你 7 个问题 → 自动 clone → 跑安装器 → 填 key → 生成配置 → 跑验证，全程你只需要回答问题

**agent 会问你的 7 个问题**（提前想一下答案）：

1. 装到哪个目录？（推荐：当前项目下的 `./daily-watchlist/`）
2. 主要关注哪个市场？（`US` / `CN` / `HK` / `Mixed`）
3. 你的 `FMP_API_KEY` 是什么？
4. 是否需要 `TUSHARE_TOKEN`？（A 股/港股必需）
5. 需要写入哪些 focus areas？（投资主题标签，比如 `AI全栈`、`能源`、`航运`，3-8 个）
6. 你已经有 watchlist 吗？（没有的话用默认模板起）
7. 后续主要用哪类模型？（国际模型 `default` / 国产模型 `domestic`，后者会自动开新闻二次验证）

**小白常见问题**：

- **没装 Claude Code？** [Cursor](https://cursor.com) / [Cline](https://cline.bot) / [Windsurf](https://codeium.com/windsurf) 这些支持 Agent 模式的 IDE 同样能跑 `INSTALL-FOR-AI.md` 协议。
- **不想污染现有项目？** 告诉 agent 装到一个全新的空文件夹。
- **免费够用吗？** FMP 免费层 250 次/天，监控 100 只股票 + 宏观数据绰绰有余。
- **A 股也能监控？** 能。Tushare token 走 `.SH`/`.SZ`/`.HK` 后缀，FMP 走美股/欧股/日股。
- **日报在哪？** `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md`，agent 装完会直接告诉你。
- **怎么改关注方向？** 装完后编辑 `config/daily-watchlist.yaml` 里的 `focus_areas`。

---

<details>
<summary><b>🧑‍💻 进阶：本地脚本安装（Windows / macOS / Linux）</b></summary>

适合已经会用命令行的人。脚本已经处理了依赖安装、配置生成、CLAUDE.md 整合。

### 前置

- **Python 3.10+**（[python.org](https://www.python.org/downloads/)，Windows 记得勾选 "Add to PATH"）
- **Claude Code**（[claude.ai/claude-code](https://claude.ai/claude-code)）
- **FMP API Key**（[免费注册](https://site.financialmodelingprep.com/register)）
- 可选：**Tushare token**（[tushare.pro](https://tushare.pro/register)），A 股/港股必需

### Windows PowerShell

```powershell
# 如果 PowerShell 阻止脚本，先执行一次（只需一次）：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
.\.daily-watchlist-tmp\scripts\install.ps1 -TargetDir .\daily-watchlist
```

### macOS / Linux bash

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
bash ./.daily-watchlist-tmp/scripts/install.sh --target-dir ./daily-watchlist
```

### 装完之后

1. 编辑 `./daily-watchlist/config/daily-watchlist.env`，填 `FMP_API_KEY`（可选 `TUSHARE_TOKEN`）
2. 按需编辑 `./daily-watchlist/config/daily-watchlist.yaml`（market、模块开关、focus_areas）
3. 在 Claude Code 里说 `/dw-import` 导入股票池，说 `/dw-today` 生成第一份日报
4. 清理临时目录：`rm -rf .daily-watchlist-tmp`（或 `Remove-Item -Recurse .daily-watchlist-tmp`）

> 安装器检测到首次安装 `FMP_API_KEY` 未填是正常状态，不算失败。填完再跑 `python ./daily-watchlist/scripts/check_setup.py` 验证。

</details>

<details>
<summary><b>🛠️ 进阶：手动安装（5 分钟）</b></summary>

只想弄清楚每一步发生了什么的话走这条。

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
pip install -r requirements.txt
```

然后手动：

1. 新建一个工作目录，比如 `~/my-investment/`
2. 把以下结构复制过去：
   ```
   my-investment/
   ├── config/
   │   ├── daily-watchlist.env            # 从 config/daily-watchlist.env.example 复制，填 FMP_API_KEY
   │   ├── daily-watchlist.yaml           # 从 config/daily-watchlist.example.yaml 复制，改 market/focus_areas
   │   └── daily-watchlist-watchlist.md   # 从 config/daily-watchlist.watchlist.example.md 复制，加你的股票
   ├── scripts/
   │   ├── fetch_market_data.py
   │   ├── fetch_macro_data.py
   │   ├── check_setup.py
   │   ├── generate_daily_report.py
   │   └── workspace_paths.py
   ├── templates/
   │   └── daily-watchlist-report-template.md
   └── .claude/
       └── skills/
           ├── dw-today.md
           └── dw-import.md
   ```
3. 在 `my-investment/CLAUDE.md` 里写入（让 Claude Code 找到 skills）：
   ```markdown
   # Workspace Instructions

   ## Daily Watchlist

   For Daily Watchlist requests, prefer /dw-today and /dw-import.

   Read these first:
   - ./.claude/skills/dw-today.md
   - ./.claude/skills/dw-import.md
   - ./config/daily-watchlist.yaml
   - ./config/daily-watchlist-watchlist.md
   ```
4. `cd my-investment && python scripts/check_setup.py`，所有项绿色就 OK
5. Claude Code 里说 `/dw-import` → `/dw-today`

> 推荐用一键脚本（上面那个折叠块）或 AI agent 协议。手动装容易漏 `.claude/skills/` 这类隐藏目录。

</details>

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
- 查询公司名、市值、行业（A 股/港股自动走 Tushare，美/欧/日股走 FMP）
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

### 数据源

#### 内置数据源

| 服务 | 用途 | 状态 | 费用 |
|------|------|------|------|
| [FMP](https://site.financialmodelingprep.com/register) | 美/欧/日股行情 + 财报日历 | 🟢 默认启用（必需） | 免费 250 次/天 |
| [Tushare](https://tushare.pro/register) | A 股（`.SH`/`.SZ`）+ 港股（`.HK`） | 🟡 填 token 即启用（A 股/港股必需） | 免费 |

> **2026-04-17 起**：`--profile` 模式下，`.SH`/`.SZ`/`.HK` 后缀的 ticker 强制走 Tushare 而不是 FMP。FMP 对 A 股覆盖不完整（比如 `601857.SH` 中国石油拿不到），Tushare 是 A 股/港股的权威源。

#### 备选兜底数据源

下面几个都是我自己踩过坑用过的，各有优劣。脚本会在 FMP 没返回某个 ticker 时，按下表顺序自动兜底（只要对应 key 填好或包装好）：

| 服务 | 覆盖 | 状态 | 费用 | 踩过的坑 |
|------|------|------|------|----------|
| [Stooq](https://stooq.com) 实时报价（`/q/l/` 端点） | 美股、日股、德股 | 🟢 零配置自动兜底 | 完全免费，无需 key | **不支持港/韩/芬兰**；`/q/d/l/` 历史端点 2026 起要 apikey，这里只用不要 key 的 light 端点 |
| [Finnhub](https://finnhub.io/register) | 美股实时报价 | 🟡 填 `FINNHUB_API_KEY` 自动启用 | 免费 60 req/min | 免费层只覆盖美股；**不要用它拉 GLD/USO/COPX 等大宗商品 ETF**，报价严重偏离现货（我们踩过这个坑） |
| [EOD Historical Data](https://eodhd.com/) | 港股（`.HK`）、韩国（`.KO`）、芬兰（`.HE`）等 Stooq/Tushare 覆盖不到的市场 | 🟡 填 `EOD_API_KEY` 自动启用 | 免费层 20 req/day | 免费层很紧，适合小仓位兜底；付费档起步 $20/月 |
| [yfinance](https://pypi.org/project/yfinance/)（Yahoo Finance 非官方包） | 全球股票 + 历史 | 🔵 `pip install yfinance` + 设置 `ENABLE_YFINANCE=1` 才启用 | 免费无 key | **国内访问不稳定**，实测经常返回 `No price data found` — 建议有稳定 VPN 或海外 IP 再开 |
| [AKShare](https://akshare.akfamily.xyz/) | A 股 + **大宗商品期货**（COMEX 黄金、WTI 原油、LME 铜）| 🔵 需要自己改 `scripts/fetch_market_data.py` 对接 | 开源免费，无需 key | 返回格式不稳定、列名会变；主要用来补期货/外盘商品，不建议当股票 quote 主路径 |

**状态说明**：🟢 零配置即用 / 🟡 填一个 key 或装一个包就启用 / 🔵 需要手动改脚本或让 Claude Code 帮你接

#### 如何启用备选兜底

在 `config/daily-watchlist.env` 里按需加：

```env
# 必需
FMP_API_KEY=your_fmp_key

# 可选
TUSHARE_TOKEN=            # A 股 / 港股
FINNHUB_API_KEY=          # 美股 FMP 兜底
EOD_API_KEY=              # 港/韩/芬兰 兜底
ENABLE_YFINANCE=          # 设为 1 启用（需 pip install yfinance，国内慎用）
```

填上脚本会自动生效。Stooq 无需任何配置，已默认开启 US/JP/DE 自动兜底。

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
> **Status**: MVP. You maintain the watchlist and focus areas; Claude handles data, news, and reports.
> **Release**: [Latest](https://github.com/Benboerba620/daily-watchlist/releases) | [Changelog](./CHANGELOG.md)

**Keywords**: AI stock watchlist, portfolio monitoring, stock mover detection, earnings tracker, daily stock report, investing workflow, Claude Code, watchlist automation

## Who Is This For?

- You want an **AI stock watchlist** without building a full investing dashboard from scratch
- You want one repeatable workflow for **price checks, mover detection, earnings tracking, and daily research notes**
- You use **Claude Code** and want a practical investing / market monitoring tool inside it
- You already use [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) and want market updates archived into your research system

**Pick the path that matches you:**

| Who you are | Where to go |
|---|---|
| 🤖 **Let an AI agent install it (recommended)** | [Let Claude Code / an AI agent install it](#-recommended-let-claude-code--an-ai-agent-install-it) |
| 🧑‍💻 **Comfortable with CLI, want to run the scripts yourself** | [Advanced: local script install](#advanced-local-script-install-windows--macos--linux) |
| 🛠️ **Want to do every step by hand** | [Advanced: manual install](#advanced-manual-install-5-min) |

## Recent Updates
- `v1.1.0` (2026-04-24): optional `Tier` / `Hypothesis` / `Notes` watchlist columns and read-only hypothesis-linked monitoring; no holdings tracking.


- `2026-04-17`: README restructure (AI agent install promoted to primary path), installer now appends a routing pointer to the project-root CLAUDE.md, `--profile` mode routes A-shares/HK to Tushare (FMP coverage of `.SH/.SZ` is incomplete), smoke report dedup
- `v1.0.2` (2026-04-16): Added Stooq / Finnhub / EOD / yfinance quote fallbacks, documented data-source tradeoffs in README, and added optional env knobs
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

---

## Before You Start

You need a **FMP API Key** (free):

1. Go to [financialmodelingprep.com](https://site.financialmodelingprep.com/register) and register
2. Copy your API Key from the Dashboard
3. Free tier: 250 requests/day, more than enough for personal use

For **A-shares or HK stocks**, also get a Tushare token (recommended — FMP coverage of A-shares is incomplete):
- Register at [tushare.pro](https://tushare.pro/register)

> 💡 **Hit the FMP 250/day cap, or a ticker FMP doesn't cover?** The script has a built-in fallback chain: **Stooq** (zero-config, US/JP/DE), **Finnhub** (key-to-enable, US), **EOD** (key-to-enable, HK/KR/FI), **yfinance** (opt-in, unstable in mainland CN). Coverage, free tiers, and real caveats for each source: see the [Data Sources](#data-sources) section below.

---

## 🤖 Recommended: let Claude Code / an AI agent install it

**Why this is the easiest path**: if you're new to this kind of tool, "open a terminal + find the right command in docs + copy-paste + adjust paths" is much higher friction than "paste one URL into Claude Code." The AI agent path is nearly zero-op.

**Prerequisites** (1–3 min each):
1. Install [Claude Code](https://claude.ai/claude-code) (Cursor / Cline / Windsurf work too, as long as they support Agent mode)
2. Get a free [FMP API Key](https://site.financialmodelingprep.com/register) (1-min signup)
3. For A-shares / HK coverage, grab a [Tushare token](https://tushare.pro/register) too

**3 steps**:

1. Open your project directory (or a fresh empty folder) in Claude Code
2. Send the agent:

   > Install this for me: https://github.com/Benboerba620/daily-watchlist/blob/main/INSTALL-FOR-AI.md

3. The agent follows the [INSTALL-FOR-AI.md](./INSTALL-FOR-AI.md) protocol: asks 7 clarifying questions → clones → runs installer → fills keys → generates config → runs verification. All you do is answer questions.

**The 7 questions the agent will ask** (have answers ready):

1. Where should the workspace be installed? (default: `./daily-watchlist/`)
2. Primary market? (`US` / `CN` / `HK` / `Mixed`)
3. Your `FMP_API_KEY`?
4. Need `TUSHARE_TOKEN`? (required for A-shares / HK)
5. Which focus areas? (investment theme tags like `AI full-stack`, `Energy`, `Shipping` — 3–8 tags)
6. Do you already have a watchlist? (if not, start from the template)
7. Which model will you use day-to-day? (international `default` / domestic `domestic` — the latter auto-enables news secondary verification)

**Beginner FAQ**:

- **No Claude Code?** [Cursor](https://cursor.com) / [Cline](https://cline.bot) / [Windsurf](https://codeium.com/windsurf) also support Agent mode and can run `INSTALL-FOR-AI.md`.
- **Don't want to mix into an existing project?** Tell the agent to install into a fresh empty folder.
- **Is the free tier enough?** Yes. FMP 250 req/day covers 100+ stocks + macro.
- **Can I monitor A-shares?** Yes. Tushare handles `.SH`/`.SZ`/`.HK` suffixes; FMP handles US/EU/JP.
- **Where are my reports?** `daily-watchlist-reports/YYYY-MM/YYYY-MM-DD.md` — the agent will show you after install.
- **How to change focus areas?** Edit `focus_areas` in `config/daily-watchlist.yaml` after install.

---

<details>
<summary><b>🧑‍💻 Advanced: local script install (Windows / macOS / Linux)</b></summary>

For folks comfortable with the CLI. The scripts handle dependencies, config generation, and CLAUDE.md integration.

### Prereqs

- **Python 3.10+** ([python.org](https://www.python.org/downloads/), Windows: check "Add to PATH")
- **Claude Code** ([claude.ai/claude-code](https://claude.ai/claude-code))
- **FMP API Key** ([free signup](https://site.financialmodelingprep.com/register))
- Optional: **Tushare token** ([tushare.pro](https://tushare.pro/register)) — required for A-shares / HK

### Windows PowerShell

```powershell
# If PowerShell blocks scripts, run this once:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
.\.daily-watchlist-tmp\scripts\install.ps1 -TargetDir .\daily-watchlist
```

### macOS / Linux bash

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
bash ./.daily-watchlist-tmp/scripts/install.sh --target-dir ./daily-watchlist
```

### After install

1. Edit `./daily-watchlist/config/daily-watchlist.env` — add `FMP_API_KEY` (optional `TUSHARE_TOKEN`)
2. Optionally edit `./daily-watchlist/config/daily-watchlist.yaml` (market, module toggles, focus_areas)
3. In Claude Code, say `/dw-import` to load your watchlist, then `/dw-today` for your first report
4. Clean up: `rm -rf .daily-watchlist-tmp` (or `Remove-Item -Recurse .daily-watchlist-tmp`)

> A missing `FMP_API_KEY` on first install is expected — not a failure. After filling it, run `python ./daily-watchlist/scripts/check_setup.py` to verify.

</details>

<details>
<summary><b>🛠️ Advanced: manual install (5 min)</b></summary>

Take this path if you want to understand every step.

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
pip install -r requirements.txt
```

Then manually:

1. Create your workspace, e.g. `~/my-investment/`
2. Copy this structure over:
   ```
   my-investment/
   ├── config/
   │   ├── daily-watchlist.env            # from config/daily-watchlist.env.example, fill FMP_API_KEY
   │   ├── daily-watchlist.yaml           # from config/daily-watchlist.example.yaml, adjust market/focus_areas
   │   └── daily-watchlist-watchlist.md   # from config/daily-watchlist.watchlist.example.md, add your tickers
   ├── scripts/
   │   ├── fetch_market_data.py
   │   ├── fetch_macro_data.py
   │   ├── check_setup.py
   │   ├── generate_daily_report.py
   │   └── workspace_paths.py
   ├── templates/
   │   └── daily-watchlist-report-template.md
   └── .claude/
       └── skills/
           ├── dw-today.md
           └── dw-import.md
   ```
3. Write to `my-investment/CLAUDE.md` so Claude Code finds the skills:
   ```markdown
   # Workspace Instructions

   ## Daily Watchlist

   For Daily Watchlist requests, prefer /dw-today and /dw-import.

   Read these first:
   - ./.claude/skills/dw-today.md
   - ./.claude/skills/dw-import.md
   - ./config/daily-watchlist.yaml
   - ./config/daily-watchlist-watchlist.md
   ```
4. `cd my-investment && python scripts/check_setup.py` — all green = OK
5. In Claude Code: `/dw-import` → `/dw-today`

> Prefer the one-shot script (collapsed block above) or the AI agent protocol. Manual installs tend to miss hidden directories like `.claude/skills/`.

</details>

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

## Data Sources

### Built-in

| Service | Purpose | Status | Cost |
|---------|---------|--------|------|
| [FMP](https://site.financialmodelingprep.com/register) | US/EU/JP quotes + earnings calendar | 🟢 Enabled by default (required) | Free, 250 req/day |
| [Tushare](https://tushare.pro/register) | A-shares (`.SH`/`.SZ`) + HK (`.HK`) | 🟡 Enabled when token is set (required for A-shares / HK) | Free |

> **As of 2026-04-17**: in `--profile` mode, tickers with `.SH`/`.SZ`/`.HK` suffixes are forced through Tushare regardless of FMP availability. FMP's A-share coverage is incomplete (e.g. `601857.SH` China Petroleum isn't returned), and Tushare is the authoritative source for those markets.

### Fallback data sources

I've personally used every one of these — they have real quirks. The script auto-falls-back to them (in this order) whenever FMP doesn't return a ticker, as long as the matching key / package is available:

| Service | Coverage | Status | Cost | Caveats from real use |
|---------|----------|--------|------|-----------------------|
| [Stooq](https://stooq.com) real-time endpoint (`/q/l/`) | US, JP, DE | 🟢 Zero-config auto fallback | Free, no key | **No HK/KR/FI support**; the `/q/d/l/` history endpoint now requires an apikey (2026+), so we only use the key-less light endpoint |
| [Finnhub](https://finnhub.io/register) | US real-time quotes | 🟡 Auto fallback when `FINNHUB_API_KEY` is set | Free, 60 req/min | US-only on the free tier; **don't use it for commodity ETFs** like GLD/USO/COPX — prices deviate badly from spot (we hit this bug) |
| [EOD Historical Data](https://eodhd.com/) | HK (`.HK`), KR (`.KO`), FI (`.HE`), other markets Stooq/Tushare miss | 🟡 Auto fallback when `EOD_API_KEY` is set | Free tier: 20 req/day | Free tier is tight; paid tier starts at $20/month |
| [yfinance](https://pypi.org/project/yfinance/) (unofficial Yahoo Finance) | Global equities + history | 🔵 Enabled only when `pip install yfinance` + `ENABLE_YFINANCE=1` | Free, no key | **Unstable from mainland China** — frequently returns `No price data found`. Only turn on if you have a stable VPN or overseas IP |
| [AKShare](https://akshare.akfamily.xyz/) | A-shares + **commodity futures** (COMEX gold, WTI oil, LME copper) | 🔵 Requires manual wiring in `scripts/fetch_market_data.py` | Open-source, free, no key | Return shape and column names drift between versions; best as a futures/commodities backfill, not a primary quote source |

**Legend**: 🟢 works out of the box / 🟡 fill one key or install one package to enable / 🔵 manual wiring (or ask Claude Code to do it)

### How to enable fallbacks

Add any of these to `config/daily-watchlist.env`:

```env
# Required
FMP_API_KEY=your_fmp_key

# Optional
TUSHARE_TOKEN=            # A-shares / HK
FINNHUB_API_KEY=          # US fallback for FMP
EOD_API_KEY=              # HK / KR / FI fallback
ENABLE_YFINANCE=          # set to 1 to enable (needs pip install yfinance; flaky in mainland CN)
```

The script picks them up automatically. Stooq requires no config and is always on for US/JP/DE fallback.

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
