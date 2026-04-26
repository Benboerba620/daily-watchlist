---
description: 查看假设状态和交易概览
---

# Hypothesis Tracker 看板

查看当前所有假设状态，以及与交易记录的关系。

主触发命令：

- `/ht-status`

兼容别名：

- `/hypothesis-status`

## 工作流

1. 运行：

```bash
python {workspace}/scripts/sync_hypothesis.py --json
```

2. 如需交易概览，再运行：

```bash
python {workspace}/scripts/trade_stats.py --json
```

3. 输出：
   - 假设总数
   - 确定性概览
   - 近期需要关注的假设
   - 若有交易，补充交易统计

如果当天已经生成 `/dw-today` 日报，优先结合最新日报中的“假设联动”部分一起判断。
