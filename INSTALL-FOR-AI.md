# Daily Watchlist - AI 安装协议

当 AI 代理需要把本项目安装进现有工作区时，按下面的顺序执行。

## 核心原则

优先安装到独立子目录，例如 `./daily-watchlist/`。除非用户明确要求，否则不要直接装到一个已有复杂项目的根目录。

## 阶段 1：澄清

逐个确认：

1. Daily Watchlist 工作区安装到哪里？
   - 推荐默认值：`./daily-watchlist/`
2. 用户主要关注哪个市场？
   - `US`、`CN`、`HK`、`Mixed`
3. 用户的 `FMP_API_KEY` 是什么？
4. 是否还需要 `TUSHARE_TOKEN`？
5. 需要写入哪些 focus areas？
6. 用户是否已经有 watchlist？
7. 用户后续主要使用哪类模型？
   - 默认国际模型可保持 `default`
   - 如果是国产模型，建议设置 `reporting.model_profile: domestic` 和 `reporting.secondary_verify: true`

## 阶段 2：安装

先把仓库 clone 到临时目录，再把安装器跑到目标目录。

Windows PowerShell：

```powershell
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
.\.daily-watchlist-tmp\scripts\install.ps1 -TargetDir .\daily-watchlist
```

macOS / Linux：

```bash
git clone https://github.com/Benboerba620/daily-watchlist.git .daily-watchlist-tmp
bash ./.daily-watchlist-tmp/scripts/install.sh --target-dir ./daily-watchlist
```

## 阶段 3：补全配置

填入或调整：

- `config/daily-watchlist.env`
- `config/daily-watchlist.yaml`
- `config/daily-watchlist-watchlist.md`

安装器还会写入：

- `_daily-watchlist-protocols.md`
- `.claude/skills/daily-watchlist-today.md`
- `.claude/skills/daily-watchlist-import.md`
- `templates/daily-watchlist-report-template.md`

其中模板文件是默认输出格式。要明确告诉用户：之后可以随时自行编辑。

如果用户主要使用国产模型，还要明确告诉他：

- 新闻部分应由 Claude Code 的 WebSearch 完成
- 落到日报前必须做二次验证
- 二次验证不通过的条目应标记为“待人工确认”

## 阶段 4：与现有根 CLAUDE.md 融合

如果目标目录已经有 `CLAUDE.md`，只在末尾追加这一段轻量入口；如果已经存在，就不要重复追加：

```markdown
## Daily Watchlist Protocols

当用户要求 Daily Watchlist 工作流（`/dw-today` 或 `/dw-import`；`/watchlist-today` 和 `/watchlist-import` 是兼容别名；只有在不冲突时才使用 `/today` 和 `/import`）时，先读取：
- `./_daily-watchlist-protocols.md`
- `./config/daily-watchlist.yaml`
- `./templates/daily-watchlist-report-template.md`

报告写入 `./daily-watchlist-reports/YYYY-MM/`。默认按保存的模板输出，并告诉用户模板可以随时自行编辑。
```

如果没有 `CLAUDE.md`，创建一个只包含这段入口的最小版本即可。除非用户明确要求单文件模式，否则不要把完整协议整份塞进根 `CLAUDE.md`。

## 阶段 5：验证

运行：

```bash
python {workspace}/scripts/check_setup.py
python {workspace}/scripts/fetch_market_data.py --profile AAPL,MSFT
```

如果启用了宏观模块，再运行：

```bash
python {workspace}/scripts/fetch_macro_data.py
```

## 阶段 6：交付

告诉用户：

- 安装到了哪个目录
- 新建或修改了哪些文件
- 推荐触发词是 `/dw-today` 和 `/dw-import`
- `templates/daily-watchlist-report-template.md` 可以随时编辑
- 报告默认保存在 `daily-watchlist-reports/YYYY-MM/`
- 如果使用国产模型，建议开启二次验证并严格核对新闻事实

然后清理临时 clone 目录。
