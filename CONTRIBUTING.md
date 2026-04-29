# 贡献指南

## 基本原则

- 改动控制在小范围内，边界清晰
- 尽可能保持向后兼容
- 文件命名优先使用命名空间前缀，避免通用名
- 提交前跑 `python scripts/check_setup.py`
- 发布或提交 PR 前跑 `python scripts/preflight_public_repo.py`，确认没有 API key、本机路径、同步盘冲突文件或用户报告被带进公开仓库
- 涉及脚本改动的，在干净目录里做一次完整安装测试

## 欢迎的贡献

- bug 修复
- 安装和合并流程改进
- 文档整理
- 新的数据源适配器（保持项目的免费可用性）

## 不在范围内

- 交易执行
- 纯 GUI 功能
- 默认路径依赖付费服务的集成

## 发版流程

- 更新 `VERSION`、`CHANGELOG.md` 以及用户文档里提到版本号的地方
- 在 `main` 上提交发版 commit
- 打 annotated tag，例如 `git tag -a v1.0.1 -m "Release v1.0.1"`
- 推送 main 和 tag：`git push origin main && git push origin v1.0.1`
- GitHub Actions 的 `Release` workflow 会验证脚本，并基于 `CHANGELOG.md` 创建或更新 GitHub Release
- 如有需要，可以用 `workflow_dispatch` 手动触发 workflow，提供已有的 tag
