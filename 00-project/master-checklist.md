# 项目总工作清单

本清单只维护开发前、开发中和发布前的高层门禁，不复制单项任务的状态和验收内容。可执行的 Issue/看板任务、依赖、负责人、产出物和验收标准以[详细开发任务清单](./development-task-checklist.md)为准。

## 当前进度快照（2026-08-21）

- LinkForty Core `1.21.0` 已通过本地 Docker 环境完成一次真实短链点击和 `click_event` 投递；本地接收端已完成原始 body、Header、HMAC、字段、幂等、负向和重试验证。
- 脱敏验证报告保存在仓库外受控目录 `/private/tmp/linkforty-webhook-evidence/verification-report.json`，不纳入 Git，且不含 Secret 或完整 payload。
- LinkForty 负责人已确认正式签名、字段和重试契约（2026-08-21）；P0 Webhook 门禁和 M5-001 具备关闭条件。

## P0：开发前必须完成

- [x] 确认银行后台与 LinkForty Core 边界
- [x] 确认 Python 后端和前端真实代码目录：`bank-touchpoint-backend/`、`bank-touchpoint-frontend/`；当前仅为工程骨架
- [x] 确认 MVP 范围和不纳入项
- [x] 确认 M1～M5 负责人以及工作包 A、B 的主负责人
- [ ] 完成 Casdoor PoC，并确认 `employee_code` Claim
- [ ] 完成 LinkForty API PoC
- [x] 获取并验证真实 Webhook 样例（本地真实投递、验证和负责人正式确认已完成）
- [ ] 确认 NFC/NDEF 设备或 Mock 方案
- [ ] 确认 PostgreSQL、Redis 和环境访问权限
- [ ] 确认数据库角色和 LinkForty 只读权限
- [ ] 冻结 V1.3.2 物理模型、V3.1 模块方案、权限矩阵、API 规范、7 张表数据字典和状态机
- [ ] 配置 Git 分支保护、PR 模板和 CI 基础检查
- [ ] 为每个 Issue 关联[详细开发任务清单](./development-task-checklist.md)中的任务 ID，并确认任务状态不是“阻塞待确认”或“延期”
- [ ] 创建 Issue，明确目标、范围、验收、负责人、依赖、风险和回滚方案
- [ ] 完成 API、数据库、权限、外部集成、幂等、测试和文档影响分析
- [ ] 从最新 `main` 创建带任务号的短期分支

## P1：第一轮开发前完成

- [ ] FastAPI 工程可启动
- [ ] React 工程可启动
- [ ] PostgreSQL 可连接
- [ ] Redis 和 Worker 可启动
- [ ] Alembic 初始迁移可执行
- [ ] Casdoor JWT 可验证
- [ ] 测试用户、角色和组织已准备
- [ ] 第一条垂直业务切片已确定

## P2：开发中持续完成

- [ ] 工作包 A：M1/M2/M4 审计、组织员工和绑定生命周期闭环
- [ ] 工作包 B：M3/M5 资产内容、LinkForty 集成和访问事件闭环
- [ ] 按[详细开发任务清单](./development-task-checklist.md)逐项推进模块和横向能力任务，不以本清单替代单项验收标准
- [ ] 非编号统计与报表能力完成 M5 和 LinkForty 只读数据联调
- [ ] 每个正式模块和横向能力同步更新 API、数据、测试和验收资料
- [ ] 每个 PR 完成代码审核和 CI
- [ ] 每个阶段完成演示和阶段验收
- [ ] Commit 使用 Conventional Commits，单个 PR 只解决一个主要问题
- [ ] PR 正文填写背景、变更、影响、测试、API/数据库/权限变化、风险、回滚和关联事项
- [ ] 后端变更遵守 Router → Service → Repository；外部调用集中在 Integration
- [ ] 数据库结构变化使用新的 Alembic revision，不修改已应用 migration
- [ ] 前端只调用 `/api/v1`，并覆盖 loading、empty、error、no permission 状态
- [ ] 检查敏感信息、幂等、审计、Trace ID、日志脱敏和数据范围

## P3：上线前完成

- [ ] 权限和越权测试通过
- [x] Webhook 幂等和重放测试通过（本地真实样例和负责人正式确认已完成）
- [ ] 外部失败补偿验证通过
- [ ] 数据迁移和数据质量检查通过
- [ ] 备份恢复演练通过
- [ ] 回滚演练通过
- [ ] 监控和告警生效
- [ ] 生产配置审核完成
- [ ] MVP 验收矩阵关闭
- [ ] 按[详细开发任务清单](./development-task-checklist.md)关闭发布前验收、运维和回滚任务，并保留证据链接
- [ ] PR CI 全部通过，至少一名 Reviewer 批准，`BLOCKER`/`MAJOR` 已清零
- [ ] 数据库、权限、安全、外部接口和生产配置变更已获得对应 CODEOWNER 审核
- [ ] 文档、OpenAPI、数据字典、权限矩阵、迁移和发布说明已同步
- [ ] 测试环境冒烟通过，版本标签、监控点和回滚步骤已记录

## Definition of Done

- [ ] Issue 验收条件满足，范围外内容未混入
- [ ] 代码、测试、配置、文档和迁移保持一致
- [ ] CI 覆盖后端 Ruff/mypy/pytest、前端 lint/typecheck/test/build 或已记录例外
- [ ] PR 已通过 Review、无未解决阻塞项、分支无冲突
- [ ] 发布负责人确认风险、依赖、监控和回滚方案

## 当前待确认项

| 事项 | 负责人 | 截止时间 | 状态 |
|---|---|---|---|
| 银行后台 Python/React 工程目录及实现状态 | 待指定 | 2026-08-19 | 已确认目录；业务闭环待开发 |
| Casdoor issuer/audience/JWKS/employee_code Claim | 平台/安全 | 待指定 | 待确认 |
| LinkForty API 契约 | LinkForty 负责人 | 待指定 | 待确认 |
| Webhook 签名和事件样例 | LinkForty 负责人 | 待指定 | 本地真实样例已验证；负责人正式确认已完成 |
| NFC 设备和 NDEF 方案 | 硬件/业务 | 待指定 | 待确认 |
| 数据库部署和只读账号 | 数据库/运维 | 待指定 | 待确认 |
