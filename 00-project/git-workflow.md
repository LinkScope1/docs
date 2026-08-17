# Git 工作流

## 分支

```text
main        生产稳定代码
develop     集成分支
feature/*   新功能
fix/*       普通缺陷
hotfix/*    生产紧急修复
```

每个分支必须关联一个任务编号，例如：

```text
feature/M3-001-touchpoint-assets
fix/M7-004-webhook-idempotency
```

## 合并规则

- `main` 禁止直接推送。
- 所有变更通过 Pull Request 合并。
- PR 必须关联 Issue 或任务。
- CI、测试和必要审核通过后才能合并。
- 数据库、权限、外部接口和安全代码需要对应 CODEOWNER 审核。
- 合并后删除已完成分支。

## Commit

使用 Conventional Commits：

```text
feat(M3): add touchpoint asset creation
fix(M7): handle duplicate webhook event
docs(api): update assignment contract
test(M4): add transfer snapshot cases
refactor(auth): extract permission dependency
chore(ci): update test pipeline
```

## 禁止事项

- 提交密码、Token、Webhook Secret 或生产配置。
- 未经审核直接修改生产配置。
- 将多个无关功能混在一个 PR。
- 用重写历史掩盖已发布的错误提交。
