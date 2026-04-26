---
description: 记录交易并回写假设
---

# Hypothesis Tracker 记录交易

记录交易，并把交易动作回写到假设上下文。

主触发命令：

- `/ht-trade`

兼容别名：

- `/hypothesis-trade`

## 工作流

1. 解析用户的自然语言交易描述，提取：
   - ticker
   - action
   - shares
   - price
   - market
   - reasoning
2. 追问缺失信息：
   - 关联哪个 hypothesis
   - kill thesis / stop loss
   - 卖出时的 outcome note
3. 追加到 `portfolio/trades.csv`
4. 更新 `portfolio/holdings.csv`
5. 如已关联 hypothesis，在对应假设文件中补一条证据或确定性变化说明
6. 如有必要，在 `portfolio/journal/YYYY-MM-DD.md` 追加交易日志

如果今天的交易来自 `/dw-today` 报告里的信号，明确写出来。
