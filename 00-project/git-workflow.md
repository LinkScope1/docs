# Git 工作流入口

完整、唯一的协作开发规则见 [MVP 项目开发与 Pull Request 协作规范](./development-workflow.md)。本文件只保留日常执行入口，避免与主规范形成两份需要同步维护的制度。

## 快速规则

- `main` 是唯一默认集成分支，禁止直接 Push 和 Force Push。
- 任务从最新 `main` 创建短期分支：`feature/*`、`fix/*`、`hotfix/*`、`docs/*`、`refactor/*`、`test/*`、`chore/*`。
- 每个分支关联 Issue 或任务，每个 PR 只解决一个主要问题。
- 合并前必须通过 CI、完成 Review、解决 `BLOCKER`/`MAJOR`，数据库、权限、安全和外部接口变更必须经过对应 CODEOWNER。
- 默认 Squash and Merge，合并后删除短期分支。
- Commit 使用 `type(scope): description` 的 Conventional Commits 格式。

创建和同步示例：

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/M3-001-touchpoint-assets
git fetch origin
git rebase origin/main
```

提交前检查 `git status`、`git diff --check`、完整 diff 和敏感信息。冲突由 PR 作者解决并重新运行检查。
