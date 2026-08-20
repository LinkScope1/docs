# 代码审查和安全审查模板

完整协作规则见 [MVP 项目开发与 Pull Request 协作规范](../00-project/development-workflow.md)。本模板用于执行审查，不替代主规范。

```text
请审查当前分支相对于目标分支的变更。

目标分支：
[main 或其他分支]

重点检查：
- 业务逻辑正确性
- 权限绕过和数据范围越权
- SQL 注入和不安全查询
- JWT、Token、密码和 Secret 泄露
- Webhook 重放和签名绕过
- 幂等漏洞
- 事务不完整
- 外部调用失败处理
- 数据库迁移和回滚风险
- 测试缺失
- 是否违反 AGENTS.md 和 docs 设计基线

补充检查：

- 是否一个 PR 只解决一个主要问题，是否混入无关格式化或重构；
- API 是否先同步 `docs/03-api/openapi.yaml`，前后端类型是否一致；
- 数据库结构是否使用新的 Alembic migration，是否说明锁表、数据量和回滚；
- LinkForty 写入是否只走 API，是否越过外部表边界；
- 前端是否只调用银行后台 `/api/v1`，是否覆盖 loading、empty、error、no permission；
- CI 是否覆盖 Lint、类型检查、测试和构建，未执行的检查是否有原因。

每个问题必须包含：
- 严重级别：BLOCKER / MAJOR / MINOR / SUGGESTION / QUESTION
- 文件路径和代码位置
- 问题描述
- 影响范围
- 修复建议

`BLOCKER` 和 `MAJOR` 必须在合并前解决或由技术负责人记录豁免；`MINOR`、`SUGGESTION` 和 `QUESTION` 需要明确是否处理。若没有发现问题，也要说明审查范围、执行的检查和未覆盖的内容。
```
