# 项目总工作清单

本清单只维护开发前、开发中和发布前的高层门禁，不复制单项任务的状态和验收内容。可执行的 Issue/看板任务、依赖、负责人、产出物和验收标准以[详细开发任务清单](./development-task-checklist.md)为准。

## 当前进度快照（2026-08-24）

- LinkForty Core `1.21.0` 已通过本地 Docker 环境完成一次真实短链点击和 `click_event` 投递；本地接收端已完成原始 body、Header、HMAC、字段、幂等、负向和重试验证。
- 脱敏验证报告保存在仓库外受控目录 `/private/tmp/linkforty-webhook-evidence/verification-report.json`，不纳入 Git，且不含 Secret 或完整 payload。
- LinkForty 负责人已确认正式签名、字段和重试契约（2026-08-21）；P0 Webhook 门禁和 M5-001 具备关闭条件。
- Webhook Secret provisioning 方案已确认：配置服务一次性调用 Core 现有管理 API 获取 Secret；配置服务联调、网络访问审计和生产配置接入仍待实施与验收。
- Casdoor 真实认证/权限外部联调和 NFC 真机/SDK/写卡读回核验延期至 V1.4；V1.3.2 仅保留 `AccessContext`、`MockAccessContextProvider`、`NfcDevice` 和 `MockNfcDevice` 的开发/测试边界，未配置真实认证的生产环境必须拒绝访问，因此 V1.3.2 不能作为生产版本发布。
- V1.3.2 内部数据语义、幂等边界、M4 规则、导入/导出范围和统计口径已按冻结记录收敛；LinkForty API/只读权限、真实数据库/Redis 环境和发布证据仍需外部证据。Core 不处理 `Idempotency-Key` 的重复 Link 行为作为 V1.3.2 已知风险接受，不标记为幂等通过。
- M4 绑定、解绑和调拨已补齐 Router → Service → Repository 的本地事务边界，继续使用既有 OpenAPI 路径和 7 张银行表；真实 M2 主数据、PostgreSQL 并发和发布证据仍未关闭。
- 本次自动化验证已通过：银行后端 93 项通过；Ruff/mypy、前端 lint/typecheck/build、LinkForty Core 188 项测试和文档校验均通过。Docker 中的银行 PostgreSQL/Redis 与 LinkForty Core/Redis 健康检查已通过，但银行数据库当前 revision 为 `0002`、`bank_linkforty_ro` 角色不存在，且银行后台/Worker 未在该 Compose 环境运行；相关迁移、只读权限、队列隔离和生产配置证据不关闭。
- LinkForty 本地真实 API 的重复请求验证发现：相同 `Idempotency-Key` 产生两个不同 Link，临时测试资源已清理；该结果作为 V1.3.2 已知缺陷记录，不作为幂等通过，也不创建 V1.4 修复任务。正式字段、TLS/ACL 和只读权限门禁仍待外部证据。

## P0：开发前必须完成

- [x] 确认银行后台与 LinkForty Core 边界
- [x] 确认 Python 后端和前端真实代码目录：`bank-touchpoint-backend/`、`bank-touchpoint-frontend/`；当前仅为工程骨架
- [x] 确认 MVP 范围和不纳入项
- [x] 确认 M1～M5 负责人以及工作包 A、B 的主负责人
- [ ] 完成 Casdoor 真实环境 PoC，并确认 `employee_code` Claim（延期至 V1.4；V1.3.2 保留开发/测试 Mock）
- [x] 完成 LinkForty API PoC
- [x] 获取并验证真实 Webhook 样例（本地真实投递、验证和负责人正式确认已完成）
- [x] 确认 NFC/NDEF Mock 方案（真实设备、SDK、写卡和读回核验延期至 V1.4）
- [ ] 确认 PostgreSQL、Redis 和环境访问权限（本地容器健康；迁移 revision、银行后台/Worker 和生产访问证据待补）
- [ ] 确认数据库角色权限（本地单账号配置可用于测试；生产权限分离及 LinkForty 只读账号证据待补）
- [ ] 冻结 V1.3.2 物理模型、V3.1 模块方案、权限矩阵、API 规范、7 张表数据字典和状态机（见 [V1.3.2-FREEZE-001](./v1.3.2-freeze-001.md)；外部证据门禁未闭合）
- [x] 配置 Git 分支保护、PR 模板和 CI 基础检查
- [ ] 为每个 Issue 关联[详细开发任务清单](./development-task-checklist.md)中的任务 ID，并确认任务状态不是“阻塞待确认”或“延期”
- [ ] 创建 Issue，明确目标、范围、验收、负责人、依赖、风险和回滚方案
- [ ] 完成 API、数据库、权限、外部集成、幂等、测试和文档影响分析
- [ ] 从最新 `main` 创建带任务号的短期分支

## P1：第一轮开发前完成

- [x] FastAPI 工程可启动
- [x] React 工程可启动
- [ ] PostgreSQL 可连接（本地 PostgreSQL 15.19/`bank_admin` 已验证；迁移和生产权限待补）
- [ ] Redis 和 Worker 可启动（本地 Redis 7.4.11 已验证；Worker、队列隔离和生产配置待补）
- [x] Alembic 初始迁移可执行
- [ ] Casdoor 真实 JWT 可验证（延期至 V1.4；开发/测试使用 Mock `AccessContext`）
- [x] 测试用户、角色和组织已准备
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
| Casdoor issuer/audience/JWKS/employee_code Claim | 平台/安全 | V1.4 | 延期至 V1.4；真实外部证据待补 |
| LinkForty API 契约 | LinkForty 负责人 | 待指定 | 本地创建/查询和健康检查可用；同 Key 重复请求产生两个 Link，作为 V1.3.2 已知风险；正式字段、TLS/ACL 和只读证据待确认 |
| Webhook 签名和事件样例 | LinkForty 负责人 | 待指定 | 本地真实样例已验证；负责人正式确认已完成 |
| NFC 设备和 NDEF 方案 | 硬件/业务 | V1.4 | 延期至 V1.4；真实外部证据待补，V1.3.2 使用 Mock |
| 数据库部署和只读账号 | 数据库/运维 | 待指定 | PostgreSQL 15.19/Redis 7.4.11 健康；Alembic 当前 `0002`、`bank_linkforty_ro` 不存在，迁移权限和只读负向证据待确认 |
