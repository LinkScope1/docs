# Codex 任务提示词模板

本目录用于统一团队使用 Codex 开展银行触点载体管理系统的分析、开发、测试、审查、文档和运维工作。

## 使用方式

1. 先确认任务类型。
2. 复制对应模板。
3. 填写任务目标、范围、相关文件和验收标准。
4. 在新对话中说明是否允许修改文件。
5. 要求 Codex 提供代码证据和实际测试结果。

## 模板索引

| 模板 | 使用场景 |
|---|---|
| [01-new-conversation](./01-new-conversation.md) | 新建对话、加载项目背景 |
| [02-repository-analysis](./02-repository-analysis.md) | 只读分析代码库和文档 |
| [03-feature-development](./03-feature-development.md) | 开发 M1～M8 业务功能 |
| [04-backend-api-and-database](./04-backend-api-and-database.md) | Python 后端、API 和数据库 |
| [05-frontend-development](./05-frontend-development.md) | React 前端页面和交互 |
| [06-external-integration](./06-external-integration.md) | Casdoor、LinkForty、Webhook、NFC |
| [07-testing-and-acceptance](./07-testing-and-acceptance.md) | 测试计划、测试实现和验收 |
| [08-bug-diagnosis](./08-bug-diagnosis.md) | Bug 定位、修复和回归测试 |
| [09-code-review-and-security](./09-code-review-and-security.md) | 代码审查和安全审查 |
| [10-documentation-and-adr](./10-documentation-and-adr.md) | 编写文档和 ADR |
| [11-release-and-operations](./11-release-and-operations.md) | 部署、发布、监控和回滚 |

## 通用提示词结构

```text
项目背景
任务目标
相关文档
当前代码范围
包含范围
不包含范围
约束条件
实施要求
验收标准
测试要求
最终汇报格式
```

## 统一要求

```text
先检查当前代码和文档，不要假设设计已经实现。
如果文档与代码冲突，必须显式列出冲突。
如果无法确认，不得编造结论，标记为待确认并给出推荐默认方案。
如果是分析任务，不得修改任何代码或文档。
如果是开发任务，只修改任务范围内的文件。
完成后必须说明实际修改、测试结果、未完成项和风险。
不得输出虚假的测试结果。
```

## 任务边界建议

- 一次对话只处理一个主要目标。
- 开发任务必须填写不包含范围。
- 高风险任务先要求分析，再授权实施。
- 涉及权限、迁移、外部调用和生产配置时必须提供验收标准。
