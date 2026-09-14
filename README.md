# 银行触点载体管理系统协作资料

本目录包含银行触点载体管理系统的产品、架构、接口、数据、安全、开发、测试、部署和运维资料。

## 资料基线

- [MVP 功能模块划分分析方案 V3.1](./01-product/mvp-module-plan.md)
- [数据物理模型与数据字典 V1.3.2](./04-database/data-dictionary.md)
- [项目目录建设与说明 V2.0](./00-project/project-directory-guide.md)
- [ADR-004：M3 可复用地址页面主数据](./adr/ADR-004-reusable-address-pages.md)

以上三份 Markdown 是可编辑主版本来源。现有对应 DOCX 保留为只读历史/发布归档，不与 Markdown 双向手工维护；如需 DOCX，按 Markdown 主版本导出。

原始 DOCX 统一归档在 [`archive/baselines`](./archive/baselines/) 下，并按文档系列分类；归档文件不作为编辑来源。

V1.3.2 是 8 张银行业务表、横向批量导入任务表、字段、状态和外部数据边界的权威来源；V3.1 是 M1～M5 模块编号、职责、数据所有权和双人研发工作包的权威来源。两者冲突时，数据结构以 V1.3.2 为准，模块编号以 V3.1 为准。M3 的 `touchpoint_address_pages` 是可复用地址页面主数据，不属于 `target_resources` 或 `routing_rules`。

V2.0 是当前工作区目录边界、后端和前端目标落点、现有/目标/迁移期/禁止新建状态标记及双人研发目录工作包的权威说明；它不代表目录中的业务功能已经实现。

其他 Markdown 文档用于描述当前规则、架构、接口、权限、测试、部署和运维；如内容存在不一致，以以上三份基线为准。

## 开发治理规范

- [团队协作者项目阅读指南](./00-project/collaborator-onboarding-guide.md)：新协作者的首次阅读路径、项目边界、事实判断和第一个 PR 操作指南。
- [MVP 项目开发与 Pull Request 协作规范](./00-project/development-workflow.md)：唯一协作开发主规范，覆盖 Issue、分支、Commit、PR、Review、测试、API、数据库、CI、发布、回滚和 AI 协作。
- [Git 工作流快速入口](./00-project/git-workflow.md)：只保留日常命令和规则摘要，完整规则以主规范为准。
- [项目总工作清单](./00-project/master-checklist.md)：开发前、开发中、发布前门禁。
- [详细开发任务清单](./00-project/development-task-checklist.md)：将需求拆分为可直接创建 Issue、看板卡片和验收项的任务明细。

推荐阅读顺序：先读本文件和 [团队协作者项目阅读指南](./00-project/collaborator-onboarding-guide.md)，再读 [项目章程](./00-project/project-charter.md)、[协作开发主规范](./00-project/development-workflow.md)、[总工作清单](./00-project/master-checklist.md)、[详细开发任务清单](./00-project/development-task-checklist.md) 和任务相关的产品、架构、API、数据库、安全文档。开发、测试和发布任务必须继续核对对应任务 ID、依赖和验收标准。

## 目录

- `00-project`：项目范围、职责、Git 工作流和总清单
- `01-product`：术语、业务规则和 MVP 验收范围
- `02-architecture`：系统架构、技术选型和非功能需求
- `03-api`：接口规范和外部系统契约
- `04-database`：数据库、数据字典、状态机和权限
- `05-security`：认证、权限、安全和审计
- `06-frontend`：前端开发与页面规范
- `07-backend`：Python 后端分层、事务、任务和日志规范
- `08-testing`：测试策略和验收矩阵
- `09-deployment`：环境、部署、发布和回滚
- `10-operations`：监控、运维、备份和故障处理
- `11-codex-prompts`：Codex 新建对话、分析、开发、测试、审查、文档和发布提示词模板
- `adr`：架构决策记录

## Codex 提示词模板

使用 [Codex 任务提示词模板](./11-codex-prompts/README.md) 选择对应的任务模板。模板要求先读取项目事实、明确任务边界、区分已实现与待开发，并在完成后报告实际修改和验证结果。

## 状态标记

- `已确认`：有文档、代码或外部系统证据支持
- `待确认`：必须由产品、平台、安全或外部系统负责人确认
- `建议`：技术团队推荐方案，不等同于业务承诺
- `阻塞`：未确认前不能进入依赖该决策的开发或验收
