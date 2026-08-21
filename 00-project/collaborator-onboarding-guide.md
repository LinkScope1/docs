# 团队协作者项目阅读指南

> 适用对象：第一次接触本项目的产品、后端、前端、测试、安全、数据库、运维和外部系统协作者。
>
> 阅读目标：在开始改代码或提 PR 前，能够说明项目做什么、哪些内容是当前基线、自己应该修改哪个仓库，以及怎样完成一次合规协作。

## 1. 先记住这五句话

1. `docs/` 是产品、架构、API、数据库、安全、测试和发布资料的权威仓库。
2. 当前正式业务模块为 M1～M5；统计与导出是无编号横向能力。
3. `bank-touchpoint-backend/`、`bank-touchpoint-frontend/`、`docs/` 和 `.github/` 是独立 Git 仓库，分别维护历史、分支和 PR。
4. LinkForty Core 是外部系统；银行后台对它的写入只能通过 API，不能直接改它的数据库或复制它的源码。
5. 任何开发都从 Issue 和最新 `main` 开始，一个 PR 只解决一个主要问题，合并前必须通过 CI 和 Review。

## 2. 项目是什么

这是一个银行 NFC 触点载体管理系统，负责管理 NFC 触点资产、载体内容、员工绑定、访问事件和操作审计。

当前业务模块和数据对象如下：

| 模块 | 你需要理解的业务 | 银行侧主要表 |
|---|---|---|
| M1 | 后台访问上下文、操作审计 | `operation_logs` |
| M2 | 组织、员工和数据范围 | `organization_units`、`employees` |
| M3 | NFC 触点资产和载体内容 | `touchpoint_assets`、`touchpoint_payloads` |
| M4 | 载体与员工的绑定、解绑、转交和历史 | `touchpoint_employee_assignments` |
| M5 | 访问事件接入、幂等投影和关联 | `access_events` |

## 3. 工作区怎么划分

| 目录 | 作用 | 第一次协作时的判断 |
|---|---|---|
| `docs/` | 规范、契约、基线和协作资料 | 产品/API/数据/权限问题先在这里找依据 |
| `bank-touchpoint-backend/` | Python 3.11+、FastAPI、SQLAlchemy、Alembic 后端 | 只实现银行后台服务，不直接操作 LinkForty 表 |
| `bank-touchpoint-frontend/` | React、TypeScript、Vite 管理后台 | 只调用银行后台 `/api/v1`，不连接数据库或 LinkForty |
| `.github/` | 工作区治理说明 | 管理协作边界，不承载业务代码 |
| `linkforty/core/` | 独立 TypeScript/Fastify 外部系统 | 遵守它自己的贡献和发布规则，不随手修改 |
| `card-switch-demo/` | 演示项目 | 仅用于演示，不证明银行 MVP 已实现 |

每个目录中的 Git 历史独立。跨仓库功能要拆成多个 PR，并在 PR 中相互引用 Issue、依赖 PR 和发布顺序；不要把多个目录当成一个可以统一提交的仓库。

## 4. 第一次阅读顺序

### 第一步：建立全局认识

按下面顺序阅读，先不要急着改代码：

1. 本指南：了解阅读路径和协作边界。
2. [docs README](../README.md)：确认三份 Markdown 基线、DOCX 归档位置和资料目录。
3. [项目章程](./project-charter.md)：确认项目目标、范围和不纳入项。
4. [MVP 模块方案](../01-product/mvp-module-plan.md)：理解 M1～M5、数据所有权和研发工作包。
5. [业务规则](../01-product/business-rules.md)：理解状态、幂等、员工、绑定和事件规则。

读完后，你应该能回答：系统管理什么、当前有效模块有哪些、哪些系统属于外部边界、哪些旧内容不能继续新建。

### 第二步：理解协作制度

1. [MVP 开发与 PR 协作主规范](./development-workflow.md)：唯一完整规则来源。
2. [Git 工作流入口](./git-workflow.md)：分支、同步和 Commit 快速命令。
3. [角色与职责](./roles-responsibilities.md)：确认谁负责需求、Review、CODEOWNER、发布和外部系统。
4. [项目总工作清单](./master-checklist.md)：确认开发前、开发中和发布前门禁。
5. [详细开发任务清单](./development-task-checklist.md)：选择任务 ID，查看状态、依赖、负责人、产出物和验收标准。
6. 当前仓库的 `.github/pull_request_template.md`、`CODEOWNERS` 和 CI：了解实际执行字段。

不要把 PR 模板当成完整制度；模板是填报入口，主规范才是唯一规则来源。

### 第三步：按任务阅读技术资料

| 任务类型 | 必读资料 |
|---|---|
| 后端 API | [系统架构](../02-architecture/system-architecture.md)、[OpenAPI](../03-api/openapi.yaml)、[API 指南](../03-api/api-guidelines.md)、后端 `AGENTS.md` |
| 数据库或迁移 | [数据字典](../04-database/data-dictionary.md)、[ERD](../04-database/erd.md)、[数据库指南](../04-database/database-guidelines.md)、后端 Alembic 目录 |
| 前端页面 | [前端指南](../06-frontend/frontend-guidelines.md)、[页面规范](../06-frontend/page-guidelines.md)、OpenAPI、前端 `AGENTS.md` |
| 权限和审计 | [权限矩阵](../05-security/permission-matrix.md)、[数据范围](../05-security/data-scope.md)、[审计指南](../05-security/audit-guidelines.md) |
| LinkForty/Webhook | [LinkForty API](../03-api/integrations/linkforty-api.md)、[Webhook 契约](../03-api/integrations/linkforty-webhook.md)、后端 integrations 说明 |
| 测试和验收 | [测试策略](../08-testing/test-strategy.md)、[验收矩阵](../08-testing/acceptance-matrix.md) |
| 部署和发布 | [部署指南](../09-deployment/deployment-guide.md)、[发布流程](../09-deployment/release-process.md)、[回滚](../09-deployment/rollback.md) |

## 5. 怎样判断“这是事实还是规划”

项目资料中会同时出现当前文件、目标目录、接口草案和待确认事项。阅读或 Review 时按以下证据等级判断：

| 标记/证据 | 含义 |
|---|---|
| `已确认` | 有权威文档、代码、迁移、接口或测试证据支持 |
| `待确认` | 需要产品、平台、安全、数据库或外部系统负责人确认 |
| `建议` | 技术团队推荐方案，不等于业务承诺 |
| `阻塞` | 未确认前不能进入依赖该决定的开发或验收 |
| 目录或静态页面 | 只能证明工程落点或演示存在，不能证明业务闭环完成 |
| API 草稿或 OpenAPI | 证明契约设计，不自动证明后端已经实现 |
| Alembic migration | 证明有数据库演进脚本，但仍需检查是否已执行、是否有业务 API 和测试 |
| 测试通过 | 只证明被测试范围通过，不能扩大为整个模块已完成 |

任何“已实现”结论都要能指向文件路径、类/函数、接口路径、migration 或测试证据。证据不足时写“待确认”或“工程骨架”，不要凭目录名称推断完成状态。

## 6. 按角色选择阅读重点

### 产品、项目和业务协作者

优先理解项目章程、MVP 模块方案、业务规则、验收范围和变更记录。提出需求时必须说明目标模块、验收条件、不在范围、权限/数据/API 影响和回滚约束，不直接以页面名称代替业务定义。

### 后端协作者

除上述资料外，重点阅读后端 `AGENTS.md`、分层规范、事务指南、幂等指南和 integrations 说明。业务规则放在 Service，数据库访问放在 Repository，外部调用放在 Integration；数据库结构变化只能通过新的 Alembic revision。

### 前端协作者

重点阅读前端 `AGENTS.md`、前端页面/组件/权限规范和 OpenAPI。页面只调用银行后台 `/api/v1`，必须处理 loading、empty、error、no permission；前端隐藏按钮不能代替后端的权限和数据范围校验。

### 测试、安全和数据库协作者

重点关注权限与越权、数据范围、状态机、幂等、Webhook 重放、迁移回滚、敏感信息和外部失败补偿。数据库、权限、安全、外部接口和生产配置变更必须触发对应 CODEOWNER 审核。

### 外部系统和运维协作者

先确认 LinkForty、Casdoor、NFC、环境、监控、备份和回滚边界。不要在银行项目中直接执行 LinkForty 平台表的 DDL、DML、TRUNCATE 或迁移，也不要通过数据库读取、记录或输出 `webhooks.secret`；Secret 只通过受控 Core API provisioning 交付给配置服务。

## 7. 第一次进入代码仓库的操作

进入任何仓库后先执行只读检查：

```bash
git status --short --branch
git log -5 --oneline
find . -name AGENTS.md -print
```

然后阅读该仓库的 `AGENTS.md`、`README.md`、`.github/workflows/ci.yml` 和相关测试。先确认已有用户修改，不能用清理、重置或覆盖操作处理不属于自己的变更。

根据任务选择仓库：

```text
产品/API/数据/权限/协作规范 → docs/
银行后台 API/Service/迁移/Worker → bank-touchpoint-backend/
管理后台页面/组件/API 接入 → bank-touchpoint-frontend/
工作区治理文件 → .github/
```

如果需要同时修改多个仓库，先在 Issue 中写清楚跨仓库影响，再分别检查状态、创建分支、提交和验证。

## 8. 从任务到第一个 PR

### 8.1 开发前

- 创建或认领 Issue，写清背景、目标、范围、验收、负责人、依赖、风险和回滚。
- 先在[详细开发任务清单](./development-task-checklist.md)中选择或创建任务 ID，并核对任务状态、前置依赖、MVP 范围和验收标准。
- 做 API、数据库、权限、外部集成、幂等、审计、测试、部署和文档影响分析。
- 从最新 `main` 创建短期分支：`feature/*`、`fix/*`、`hotfix/*`、`docs/*`、`refactor/*`、`test/*` 或 `chore/*`。

### 8.2 开发中

- 一个 PR 只解决一个主要问题；大功能按数据库、Service、API、前端、测试和文档边界拆分。
- Commit 使用 `type(scope): description`，例如 `feat(M3): add touchpoint asset creation`。
- API 先更新 `docs/03-api/openapi.yaml`，后端实现后，前端重新生成类型并联调。
- 数据库只新增 Alembic revision，不修改已应用 migration。
- 检查权限、数据范围、幂等、Trace ID、审计、日志脱敏和外部失败处理。

### 8.3 提 PR 前

执行对应仓库 CI 命令，并在 PR 模板中填写实际结果：

```text
后端：uv run ruff check .、uv run mypy src、uv run pytest
前端：npm run lint、npm run typecheck、npm run test -- --run、npm run build
docs：python scripts/validate_docs.py、git diff --check
```

PR 必须写明背景、修改、影响范围、API/数据库/权限变化、测试、风险、监控、回滚和关联事项。普通 PR 至少一名 Reviewer；高风险路径还需要对应 CODEOWNER。

### 8.4 合并后

默认 Squash and Merge，合并后删除短期分支。发布前还要完成测试环境冒烟、版本记录、监控确认和回滚准备。跨仓库变更要确认依赖 PR 的合并和发布顺序。

## 9. 最容易踩的边界

- 不要把 `linkforty/core/` 的代码、表结构或发布规则复制到银行后台。
- 不要让前端直连数据库、Redis 或 LinkForty。
- 不要把 `target_resources`、`routing_rules`、旧模块编号或历史 DOCX 内容当作当前新增范围。
- 不要直接 Push 或 Force Push 到 `main`。
- 不要把功能、重构、格式化和依赖升级混在一个 PR。
- 不要提交密码、Token、JWT、Webhook Secret、数据库连接串或未脱敏个人信息。
- 不要通过隐藏前端菜单代替后端权限校验。
- 不要把目录、接口草稿、静态页面或单个通过的测试描述成完整业务已实现。
- 不要修改任务范围外的仓库、文件、migration 或外部表。

## 10. 建议的第一次任务

第一次协作建议选择一个边界明确的小任务，例如：

1. 为现有页面补充一个明确的 loading/error 状态测试；
2. 为后端一个已有 Service 补充幂等或权限测试；
3. 修正文档中的一个内部链接或补充一个待确认项；
4. 为一个已有 API 更新对应的 OpenAPI 描述和验证记录。

不要第一次就同时改数据库、后端、前端、外部系统和发布配置。先通过一次小而完整的 Issue → Branch → Commit → PR → CI → Review 流程，熟悉仓库边界和团队协作节奏。

## 11. 阅读完成标准

完成入门后，你应该能够回答：

- 当前正式模块是哪几个，每个模块拥有哪张银行侧表？
- API、数据库、权限和 DOCX 的权威来源分别在哪里？
- 当前任务应该修改哪个独立仓库，是否需要跨仓库 PR？
- LinkForty 写入的正确方式是什么，哪些数据库操作被禁止？
- 怎样从 `main` 创建分支、写 Commit、填写 PR 和触发 CODEOWNER？
- 需要运行哪些本地检查，什么问题会阻塞合并？
- 当前代码证据是否足以称为“已实现”？

如果其中任何一项无法回答，先继续阅读对应文档或在 Issue 中标记“待确认”，不要直接开始扩大范围的实现。

## 12. 一页速查

```text
先看：本指南 → docs/README → 项目章程 → MVP 模块方案 → 业务规则
再看：开发主规范 → Git 工作流 → 角色职责 → 总工作清单
按任务：架构 / OpenAPI / 数据字典 / 权限矩阵 / 测试 / 部署
进仓库：status → AGENTS → README → CI → 相关代码和测试
开始开发：Issue → 最新 main → 短期分支 → 小 PR
提交前：diff、secret、API/DB/权限/幂等/文档同步、CI
合并前：Review、CODEOWNER、BLOCKER/MAJOR 清零、风险和回滚
```
