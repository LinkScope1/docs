# MVP 项目开发与 Pull Request 协作规范

> 状态：项目协作主规范
>
> 适用基线：V1.3.2 数据物理模型、V3.1 MVP 模块方案、V2.0 项目目录说明
>
> 唯一编辑来源：本文件。其他仓库中的模板、入口文档和检查脚本只承载执行规则，不复制本文件的完整制度。

## 1. 目的与适用范围

本规范用于保证需求、代码、数据库、接口、测试、文档和发布变更可追踪、可审查、可回滚。目标是：

- 一个任务对应清晰的目标、负责人和验收条件；
- 一个 PR 只解决一个主要问题，保持可审查和可回滚；
- API、数据库、权限、外部集成和文档保持同步；
- `main` 始终处于可构建、可测试和可发布状态；
- 任何变更都能沿着 Issue → Branch → Commit → PR → Release 链路追踪。

本规范适用于银行后台、前端、API、SDK、数据库迁移、配置、Docker、CI、基础设施、文档、测试、演示和 POC。涉及独立仓库时，仓库仍遵守各自的 Git 历史和发布边界。

## 2. 当前项目事实与边界

当前正式业务模块只有 M1～M5：

| 模块 | 职责 | 银行侧主要对象 |
|---|---|---|
| M1 | 后台访问上下文与操作审计 | `operation_logs` |
| M2 | 组织与员工管理 | `organization_units`、`employees` |
| M3 | NFC 触点资产与载体内容 | `touchpoint_assets`、`touchpoint_payloads` |
| M4 | 触点载体与员工绑定生命周期 | `touchpoint_employee_assignments` |
| M5 | 访问事件接入、幂等投影与关联 | `access_events` |

统计与导出是无编号横向只读能力，不增加业务模块或专属表。当前基线不新增目标资源、路由规则、本地 IAM 业务表或银行业务办理量。

仓库边界如下：

- `docs/` 是产品、架构、API、数据库、安全、测试、部署和运维规范的权威仓库；`docs/03-api/openapi.yaml` 是 API 主契约。
- `bank-touchpoint-backend/` 是 Python/FastAPI 银行后台，使用 SQLAlchemy、Alembic、Redis/Celery 等技术基线。
- `bank-touchpoint-frontend/` 是 React/TypeScript/Vite 管理后台，只通过银行后台 `/api/v1` 访问业务 API。
- `.github/` 是根治理仓库，保存工作区级协作说明；它不承载业务代码。
- `linkforty/core/` 是独立的 LinkForty Core 外部仓库，使用 TypeScript/Fastify；银行项目不复制其源码、不修改其迁移、不直接写其平台表。
- `card-switch-demo/` 是演示项目，不代表银行后台业务已经实现，也不作为 MVP 生产实现的一部分。

银行后台对 LinkForty 的写操作必须走 API；旧编号不得用于新需求、研发任务或验收项。任何文档、代码或 Issue 都不得把目录骨架、接口草稿或静态页面描述为已实现功能。

## 3. 需求与 Issue

### 3.1 进入开发前

每项开发必须先有 Issue 或等价任务记录，至少包含：

- 背景与要解决的问题；
- 目标用户、业务模块和不在范围内的内容；
- 功能、接口、数据、权限、外部系统和非功能影响；
- 验收条件、测试数据和依赖；
- 详细开发任务清单中的任务 ID 和链接；
- 风险、回滚方式、负责人和关联文档。

需求确认后，负责人先做影响分析，再创建分支。影响分析至少覆盖 API、数据库迁移、权限与数据范围、外部集成、幂等、审计、测试、部署和文档。

### 3.2 需求变更

改变业务范围、数据模型、权限、接口契约、外部协议或发布策略时，必须更新对应规范、ADR 或变更记录。未经产品、技术和必要的安全/数据库/外部系统负责人确认，不得把建议写成已确认事实，也不得直接进入开发。

### 3.3 任务拆分

大功能按可独立审查的边界拆分，通常顺序为：

1. 数据库模型与 Alembic migration；
2. Service、Repository 和外部适配器；
3. API Router、Schema 和 OpenAPI 契约；
4. 前端 API 类型、页面和组件；
5. 单元、集成、权限、幂等和端到端测试；
6. 文档、部署和运维变更。

拆分后的 PR 仍然各自满足本规范；如必须串联，PR 描述中标注依赖顺序和暂不可合并原因。

详细任务拆分和当前状态以[详细开发任务清单](./development-task-checklist.md)为执行计划来源。任务清单不替代 OpenAPI、数据字典、权限矩阵、测试策略或其他权威规范；发现冲突时按对应权威文档处理，并在任务和变更记录中说明差异。

## 4. 工作区与仓库协作

- 每个仓库拥有独立 Git 历史、分支和发布节奏；禁止为了方便把多个仓库合并成一个 Git 历史。
- 不在一个仓库内嵌套另一个业务仓库，不提交其他仓库的 `.git`、构建产物或依赖目录。
- 跨仓库变更必须在各自仓库创建独立分支和 PR，并在 PR 中相互引用 Issue、PR 或发布记录。
- 先修改 API 主契约，再同步后端实现和前端生成类型；OpenAPI 主文件只在 `docs/` 维护。
- `linkforty/core/` 和 `card-switch-demo/` 不因银行后台任务而被顺手修改；需要外部系统变化时，先建立跨仓库任务和接口确认记录。

## 5. 分支模型

采用 `main + 短期分支` 模型，不维护长期集成分支。`main` 是唯一默认集成分支，必须始终可构建、可测试。

允许的短期分支前缀：

| 前缀 | 用途 |
|---|---|
| `feature/` | 新功能或业务能力 |
| `fix/` | 普通缺陷修复 |
| `hotfix/` | 生产紧急修复 |
| `docs/` | 文档、规范或 ADR |
| `refactor/` | 不改变外部行为的重构 |
| `test/` | 测试补充或测试基础设施 |
| `chore/` | 依赖、构建、CI 或维护工作 |

命名建议包含任务号和简短主题，例如：

```text
feature/M3-001-touchpoint-assets
fix/M5-004-webhook-idempotency
docs/CHG-005-development-workflow
chore/CI-002-frontend-lint
```

分支必须从最新 `main` 创建。短期分支完成后通过 PR 合并并删除；不在分支上长期堆积无关改动，不用重写历史掩盖已经发布的错误提交。

推荐同步方式为：

```bash
git fetch origin
git rebase origin/main
```

冲突由 PR 作者解决并重新执行本地检查。已被多人共同使用的分支不得擅自 rebase；本项目默认不创建共享长期分支。

## 6. Commit 规范

使用 Conventional Commits，格式为：

```text
<type>(<scope>): <description>
```

`scope` 可选，描述使用动词开头、简洁明确，不在一次 Commit 中混入无关主题。允许的类型：

| 类型 | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `docs` | 文档 |
| `refactor` | 重构 |
| `test` | 测试 |
| `perf` | 性能 |
| `ci` | CI 或自动化 |
| `build` | 构建和依赖 |
| `chore` | 维护 |
| `revert` | 回滚已有变更 |

示例：

```text
feat(M3): add touchpoint asset creation
fix(M5): handle duplicate webhook event
docs(workflow): define pull request gates
ci(frontend): enforce lint and build
```

提交前必须检查 `git status`、`git diff --check`、完整 diff 和敏感信息。发现密码、Token、JWT、Webhook Secret、数据库连接串、生产配置或未脱敏个人信息时，立即移除并检查 Git 历史，不能以“本地配置”理由提交。

## 7. Pull Request 规范

### 7.1 基本原则

- 每个 PR 只解决一个主要问题；功能、重构、格式化和无关修复分开提交。
- PR 应尽量小、粒度清晰。大功能按数据库、Service、API、前端、测试和文档边界拆分。
- 需求未完全实现时使用 Draft PR，先同步设计和风险，不以未完成代码阻塞正式合并。
- 标题一句话说明新增或修改了什么；正文说明为什么改、怎么改以及如何验证。
- PR 必须关联 Issue 或任务；跨仓库变更必须互相引用。PR 中必须填写任务 ID、详细任务清单链接、前置依赖及其状态和验收证据。

### 7.2 正文必填项

PR 正文必须包含：

1. 背景与目标；
2. 修改内容；
3. 影响范围和明确的不影响范围；
4. 测试命令、测试结果和未覆盖内容；
5. API、数据库、权限/数据范围、外部集成和配置变化；
6. 风险、监控点和回滚方案；
7. 关联 Issue、依赖 PR、ADR 或发布记录。

代码、配置、数据库、权限、安全、外部接口和生产配置变更，必须在正文中明确写“有/无变化”，不能留空。

### 7.3 GitHub 平台门禁

仓库管理员应为 `main` 启用：

- 禁止直接 Push 和 Force Push；
- 必须通过 Pull Request；
- 必须通过对应 CI Required Status Checks；
- 至少一名 Reviewer 审核；
- 数据库、权限、安全、外部集成和生产配置变更必须由对应 CODEOWNER 审核；
- 禁止带未解决对话或阻塞项合并；
- 合并后自动删除短期分支。

这些是 GitHub 仓库设置，文件落地后仍需管理员在平台手工启用并确认实际 Required Check 名称。

## 8. Code Review

### 8.1 审核范围

Reviewer 至少检查：

- 业务规则、边界条件、状态转换和错误处理；
- 架构分层与模块数据所有权；
- API 请求/响应、错误码、兼容性和 OpenAPI 同步；
- 数据库字段、索引、约束、事务和 migration 回滚；
- 权限、数据范围、审计、日志脱敏和安全边界；
- 幂等、Webhook 重放、并发、超时、重试和补偿；
- 测试充分性、可维护性和性能风险；
- 与本文件、`AGENTS.md` 和 docs 基线的一致性。

### 8.2 评论等级

统一使用以下标签：

- `BLOCKER`：必须修复，否则不得合并；包括数据破坏、严重安全问题、越权、核心功能错误、构建失败或不可逆迁移风险。
- `MAJOR`：高风险功能或设计问题，合并前必须解决或取得技术负责人书面豁免。
- `MINOR`：非阻塞但应修复的实现问题。
- `SUGGESTION`：可选的可读性、维护性或体验建议。
- `QUESTION`：需要作者补充事实、依据或测试结果。

MVP 合并阻塞项至少包括：功能错误、数据丢失或破坏、认证/授权/数据范围问题、安全漏洞、核心测试失败、构建失败、严重 API 不匹配、缺少必要 migration、敏感信息泄露和违反 LinkForty API-only 边界。

普通 PR 至少一名 Reviewer；数据库、权限、安全、外部接口和生产配置变更还必须有对应 CODEOWNER 审核。Reviewer 不以个人偏好阻塞符合规范的变更，争议交由技术负责人或 ADR 解决。

## 9. 合并与冲突

满足以下条件才允许合并：

- PR 作者完成自测并填写结果；
- CI 全部通过；
- 至少一名 Reviewer 批准；
- `BLOCKER` 和 `MAJOR` 数量为零；
- 分支已与最新 `main` 同步且无冲突；
- API、数据库、权限、测试、文档和发布说明已同步；
- 风险和回滚方案可执行。

默认使用 Squash and Merge，生成一个可追踪的主线提交；合并后删除短期分支。冲突由 PR 作者在自己的分支中基于最新 `main` 解决、重新测试并请求复审，不能直接覆盖他人分支或绕过 CI。

## 10. 后端分层与数据库协作

银行后台保持：

```text
Router -> Service -> Repository
                  \\-> Integration Adapter
Worker / Celery Task：异步任务、重试和补偿
```

- Router 负责协议适配和依赖注入，业务规则放在 Service。
- SQLAlchemy 和数据库访问放在 Repository。
- Casdoor、LinkForty、Webhook、NFC 等外部调用放在 Integration；不得散落在 Router。
- 后端必须强制校验权限和数据范围，不能只依赖前端隐藏菜单或按钮。
- 统一处理异常、日志、Trace ID、审计、超时、重试、幂等和补偿。

所有银行侧 schema 变化必须使用 Alembic migration；已应用的 migration 不得修改，修正必须新增 revision。数据库 PR 必须说明字段/索引/约束、数据量影响、锁表风险、部署顺序、回滚策略和验证 SQL。不得对 LinkForty 平台表执行 DDL、DML、TRUNCATE 或银行侧迁移。

事务边界由 Service 明确；外部调用不与不可回滚的数据库副作用隐式混在一个事务中。Webhook、批处理和外部 API 调用必须定义幂等键、重试、超时、重复请求和失败补偿。当前基线中 `event_id` 是全局唯一幂等键，`click_id` 只能作为非唯一逻辑引用。

## 11. API 协作

API 采用 OpenAPI-first：

1. 先在 `docs/03-api/openapi.yaml` 讨论并更新契约；
2. 后端实现 Router、Schema、权限、错误码和测试；
3. 前端生成类型并接入 `/api/v1`；
4. 联调、契约测试和文档审查通过后合并。

API 变更必须说明兼容性、调用方影响、迁移步骤、弃用周期和发布顺序。破坏性变更需要版本或兼容窗口，不能只修改后端而要求前端“自行适配”。BIGINT 通过 API 以字符串传输，UUID 保留 UUID 语义；所有写接口必须明确幂等策略。

前端禁止连接 PostgreSQL、Redis 或 LinkForty；前端权限展示不能替代后端权限校验。敏感字段不能进入前端日志、错误提示或埋点。

## 12. 配置、依赖与安全

- `.env`、本地密钥和生产配置不提交；提供脱敏的 `.env.example`。
- 不在源代码、测试输出、日志、截图、PR 或 Issue 中写入密码、Token、JWT、Webhook Secret、数据库密码或个人敏感信息。
- LinkForty `webhooks.secret` 不得读取、记录或输出；只通过受控验签适配器使用。
- 依赖升级必须说明版本、原因、兼容性、许可证和测试结果；锁文件与 manifest 同步提交。
- CI 使用最小权限，默认只读仓库内容；生产凭据通过平台 Secret 注入。
- 发现安全事件时先停止扩散、撤销凭据、保留必要证据，再按事件响应流程处理，不在公开 PR 中暴露秘密。

## 13. 测试与持续集成

测试优先覆盖核心业务、权限与数据范围、状态机、API、路由、异常、数据库、幂等、外部失败和安全边界。后端应覆盖 Schema、Service、Repository、API、外部 Mock、Webhook 并发和 migration；前端应覆盖组件、页面状态、权限展示、API 错误、集成和必要的 E2E。

每个代码 PR 的最低 CI 门禁：

- 后端：Ruff、mypy、pytest；
- 前端：ESLint、TypeScript 类型检查、测试、Build；
- docs：Markdown 链接、代码围栏、基线入口、敏感引用和 `git diff --check`；
- 依赖、Docker、契约、安全扫描和 E2E 根据风险逐步加入 Required Checks。

测试失败不得通过跳过、删除断言、放宽权限或屏蔽 CI 来“修复”。未执行的测试必须在 PR 中说明原因和补测计划。

## 14. AI 协作

AI 可以辅助分析、生成代码、测试、文档和审查，但不替代需求确认、架构决策、安全判断、人工 Review 和实际测试。使用 AI 时：

- 先提供任务边界、当前代码事实和权威文档；
- 要求 AI 只修改任务范围内的文件，并先查看 `git status` 和 diff；
- 人工确认权限、数据范围、外部调用、migration、日志脱敏和回滚；
- 要求区分已实现、部分实现和待开发，不编造接口、迁移或测试结果；
- PR 中说明 AI 参与情况（如团队要求），但责任仍由提交者和 Reviewer 承担。

## 15. 环境、发布与回滚

环境按本地开发 → 测试/演示 → 生产推进。Docker Compose 只用于本地或明确的测试场景，不把示例凭据当作生产凭据。发布流程为：

```text
PR 合并 main
  → CI 通过
  → 测试环境部署与冒烟
  → 创建版本标签
  → 发布记录
  → 生产部署
  → 健康检查、核心链路验证与监控
```

版本标签使用 `v0.x.y`；发布记录包含变更摘要、API/数据库/配置影响、迁移顺序、监控指标、已知问题和回滚步骤。回滚优先通过 revert 或重新部署已验证的稳定版本；数据库回滚必须使用已评审的逆向 migration、前向修复 migration 或备份恢复方案。紧急修复仍必须走 Git、PR、CI、审核和发布记录，不能直接改生产。

发布后至少检查健康状态、登录、M1 审计、M2 主数据、M3/M4 关键状态、M5 Webhook/事件、统计查询、错误率、延迟、队列和外部依赖。异常达到阈值时按监控和事件响应流程升级。

## 16. 文档、技术债与变更记录

实现变更必须同步相关文档：

- API 变更同步 OpenAPI、接口指南、错误码和前端生成类型；
- 数据变更同步数据字典、ERD、状态机、migration 和恢复说明；
- 权限变更同步权限矩阵、数据范围和审计说明；
- 发布/运维变更同步环境、部署、监控、备份和回滚说明；
- 跨仓库变化在各自 PR 和变更记录中相互引用。

技术债必须记录背景、影响、临时方案、偿还条件、负责人和优先级，不得以“后续优化”替代风险说明。影响业务范围、API、数据、权限或发布的决定必须进入 ADR 或 `change-log.md`。

## 17. Definition of Done

一个任务只有在以下条件全部满足时才算完成：

- Issue 的目标和验收条件已满足；
- 代码、测试、配置、文档和迁移已同步；
- 权限、数据范围、幂等、审计、日志脱敏和错误处理已验证；
- 本仓库本地检查及 CI 通过；
- PR 已完成 Review，`BLOCKER`/`MAJOR` 为零；
- 关联仓库的 PR、契约和发布顺序已明确；
- 风险、监控和回滚方案已记录；
- 合并后在测试环境完成必要冒烟，发布记录可追踪。

## 18. 最小强制规则

任何情况下都必须遵守以下底线：

1. 不直接 Push 或 Force Push 到 `main`。
2. 不提交秘密，不输出 `webhooks.secret`。
3. 不绕过 PR、Review、CI 或 CODEOWNER 门禁。
4. 不把多个无关问题混在一个 PR。
5. 不直接修改已应用 migration 或 LinkForty 平台表。
6. 不以 UI 隐藏代替后端权限和数据范围校验。
7. 不把文档、目录、接口草稿或静态页面描述为已实现功能。
8. 不报告未执行的测试，不用删除测试或关闭检查掩盖失败。
9. 不修改任务范围外的仓库、文件或业务边界。

## 19. 执行入口

- Git 分支和 Commit 快速入口：[git-workflow.md](./git-workflow.md)
- 项目负责人、Reviewer、CODEOWNER 与发布人职责：[roles-responsibilities.md](./roles-responsibilities.md)
- 研发和发布门禁：[master-checklist.md](./master-checklist.md)
- 可执行任务、依赖和验收：[development-task-checklist.md](./development-task-checklist.md)
- API 主契约：[../03-api/openapi.yaml](../03-api/openapi.yaml)
- 数据主基线：[../04-database/data-dictionary.md](../04-database/data-dictionary.md)
- 变更记录：[../01-product/change-log.md](../01-product/change-log.md)
