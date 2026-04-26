# Hypothesis Tracker 新建假设

创建一条新的投资假设文件。

主触发命令：

- `/ht-new`

兼容别名：

- `/hypothesis-new`

## 工作流

1. 读取：
   - `config/hypothesis-tracker.yaml`
   - `templates/hypothesis-tracker-hypothesis-template.md`
   - `hypothesis/` 目录
2. 收集最少必要信息：
   - 假设名称
   - 核心逻辑
   - 至少两个可证伪条件
   - 初始确定性
   - 关联标的
3. 扫描 `hypothesis/H*.md`，自动确定下一个 ID
4. 用模板生成新文件：`hypothesis/H{N}-{slug}.md`
5. 输出创建结果，并提示用户后续用 `/ht-status` 跟踪

如果用户刚做完 `/dw-today`，优先引用当天日报里出现的主题或个股来帮助建假设。
