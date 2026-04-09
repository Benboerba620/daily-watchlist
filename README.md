# Daily Watchlist

## 中文

Daily Watchlist 是一个给 Claude 使用的轻量市场监控协议包，包含：

- 行情、异动、财报、宏观数据脚本
- 日报和导入 watchlist 的 Claude skills
- 可编辑的日报模板
- 可以并入现有工作区的协议文件

### 推荐安装方式

优先安装到独立子目录，例如 `./daily-watchlist/`。

这样可以尽量避免和已有项目中的这些内容冲突：

- `.claude/skills/`
- `CLAUDE.md`
- `config/`
- `reports/`

### 默认生成的文件

安装器默认生成这些 namespaced 文件：

- `config/daily-watchlist.env`
- `config/daily-watchlist.yaml`
- `config/daily-watchlist-watchlist.md`
- `templates/daily-watchlist-report-template.md`
- `_daily-watchlist-protocols.md`
- `.claude/skills/daily-watchlist-today.md`
- `.claude/skills/daily-watchlist-import.md`
- `daily-watchlist-reports/`

Python 脚本仍兼容旧文件名：

- `config/.env`
- `config/config.yaml`
- `config/watchlist.md`

但默认优先使用 namespaced 文件。

### CLI 安装

```bash
# macOS / Linux
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
bash scripts/install.sh --target-dir ../my-project/daily-watchlist

# Windows PowerShell
git clone https://github.com/Benboerba620/daily-watchlist.git
cd daily-watchlist
.\scripts\install.ps1 -TargetDir ..\my-project\daily-watchlist
```

安装后：

1. 复制 `config/daily-watchlist.env.example` 为 `config/daily-watchlist.env`
2. 填入 API key
3. 检查 `config/daily-watchlist.yaml`
4. 检查 `config/daily-watchlist-watchlist.md`
5. 如有需要，编辑 `templates/daily-watchlist-report-template.md`
6. 运行 `python scripts/check_setup.py`
7. 运行 `python scripts/generate_daily_report.py`

### 主题新闻筛选

如果你觉得主题新闻噪音太大，可以在 `config/daily-watchlist.yaml` 里调这些字段：

- `reporting.model_profile`
- `reporting.secondary_verify`
- `reporting.theme_min_score`
- `reporting.theme_min_hits`
- 每个 `focus_area` 下的 `required_any`
- 每个 `focus_area` 下的 `exclude`

如果你使用国产模型，建议设置：

```yaml
reporting:
  model_profile: domestic
  secondary_verify: true
```

这样 Claude Code 在写日报时应启用更严格的二次验证机制，减少新闻误判和幻觉风险。

建议的流程是：

1. 第一轮 WebSearch 召回候选新闻
2. 第二轮核对来源、发布时间、正文事实和关键数字
3. 未通过二次验证的条目不要直接写入日报

### 触发词

推荐：

- `/dw-today`
- `/dw-import`

兼容别名：

- `/watchlist-today`
- `/watchlist-import`
- `/today`
- `/import`

只有在当前工作区没有冲突时，才建议使用短别名。

### 与现有工作区融合

如果你已经有自己的 `CLAUDE.md` 和 `.claude/skills/`，建议把 Daily Watchlist 保持在子目录中，只在根 `CLAUDE.md` 里加入一个轻量入口。

具体流程见 [INSTALL-FOR-AI.md](/D:/BaiduSyncdisk/Claude/daily-watchlist/INSTALL-FOR-AI.md)。

### 必需的 key

- `FMP_API_KEY`：必需
- `TUSHARE_TOKEN`：可选

## English

Daily Watchlist is a lightweight protocol pack for Claude-based market monitoring.

It includes:

- scripts for quotes, movers, earnings, and macro data
- Claude skills for daily briefing and watchlist import
- an editable report template
- a protocol file that can be merged into an existing workspace

Recommended install model:

- install into a dedicated subdirectory such as `./daily-watchlist/`

Recommended triggers:

- `/dw-today`
- `/dw-import`

Compatibility aliases:

- `/watchlist-today`
- `/watchlist-import`
- `/today`
- `/import`

Required keys:

- `FMP_API_KEY` required
- `TUSHARE_TOKEN` optional

## License

MIT
