# 项目总工作清单

本清单只维护开发前、开发中和发布前的高层门禁，不复制单项任务的状态和验收内容。可执行的 Issue/看板任务、依赖、负责人、产出物和验收标准以[详细开发任务清单](./development-task-checklist.md)为准。

## 当前进度快照（2026-09-08）

- LinkForty Core `1.21.0` 已通过本地 Docker 环境完成一次真实短链点击和 `click_event` 投递；本地接收端已完成原始 body、Header、HMAC、字段、幂等、负向和重试验证。
- 脱敏验证报告保存在仓库外受控目录 `/private/tmp/linkforty-webhook-evidence/verification-report.json`，不纳入 Git，且不含 Secret 或完整 payload。
- LinkForty 负责人已确认正式签名、字段和重试契约（2026-08-21）；P0 Webhook 门禁和 M5-001 具备关闭条件。
- Webhook Secret provisioning 方案已确认：配置服务一次性调用 Core 现有管理 API 获取 Secret；配置服务联调、网络访问审计和生产配置接入仍待实施与验收。
- Casdoor 真实认证/权限外部联调和 NFC 真机/SDK/写卡读回核验延期至 V1.4；V1.3.2 仅保留 `AccessContext`、`MockAccessContextProvider`、`NfcDevice` 和 `MockNfcDevice` 的开发/测试边界，未配置真实认证的生产环境必须拒绝访问，因此 V1.3.2 不能作为生产版本发布。
- V1.3.2 内部数据语义、幂等边界、M4 规则、导入/导出范围和统计口径已按冻结记录收敛；LinkForty API、真实数据库/Redis 环境和发布证据仍需外部证据。LinkForty 数据库只读账号、授权和负向测试明确延期至 V1.4；Core 不处理 `Idempotency-Key` 的重复 Link 行为作为 V1.3.2 已知风险接受，不标记为幂等通过。
- M4 绑定、解绑和调拨已补齐 Router → Service → Repository 的本地事务边界，继续使用既有 OpenAPI 路径和 7 张银行表；真实 M2 主数据、PostgreSQL 并发和发布证据仍未关闭。
- 本次真实 Docker 集成验收已通过：银行后端全量 `994 passed`，定向 Worker/数据库测试 `23 passed`，Ruff/mypy、Alembic 重复升级与回滚、7 张银行表、角色权限、Redis DB0/DB1/DB2、Celery `inspect ping`、测试队列 Worker、API/Worker 脱敏配置和三类任务场景均通过。脱敏报告保存在仓库外受控目录 `/private/tmp/bank-touchpoint-test-evidence/verification-report.json`，测试资源已清理；未连接生产或 LinkForty 数据库。V1.3.2 不依赖 `bank_linkforty_ro`。
- 代码复核后的任务清单统计：共 297 条；待开发 44、部分具备 154、已具备 20、已确认 19、条件开发 19、延期 28、阻塞待确认 7、已完成 5、验证中 1。状态变更仅反映可定位代码/测试证据，不代表外部环境或生产门禁已关闭。
- LinkForty 本地真实 API 的重复请求验证发现：相同 `Idempotency-Key` 产生两个不同 Link，临时测试资源已清理；该结果作为 V1.3.2 已知缺陷记录，不作为幂等通过，也不创建 V1.4 修复任务。正式字段、TLS/ACL 和 API 生产安全例外仍待外部证据。
- 当前代码已提供 M2 组织/员工生命周期、M3 资产/Payload、M4 绑定、M5 Webhook/事件、同步导入预校验、同步白名单导出和 API-only analytics 的局部实现；这些能力仍按逐项闭环、权限、数据库和外部验证结果计量，不因代码存在而整体关闭。安装/App 聚合统计已明确移出 V1.3.2，保留兼容字段和整体 `503 DATA_SOURCE_UNAVAILABLE` 失败边界，后续版本重新评估。前端 M1～M5 仍为 `ModuleStatusPage` 工程骨架，统计页是当前唯一接入银行 API 的业务页。性能报告、生产配置、备份恢复、回滚和审批仍是外部门禁。LinkForty 数据库只读脚本仅为 V1.4 准备。
- 性能/发布默认阈值已冻结：列表/事件/统计/同步导出 P95 为 500ms/1s/2s/5s，错误率 <1%，队列积压 <100，观察 30 分钟；P99 仅记录。未完成这些证据不得关闭发布任务。
- 代码复核结果：运行时 FastAPI 共 44 个 operation（含 `/health`），`/api/v1` 下 43 个；冻结 OpenAPI 为 41 个业务 operation。运行时额外存在 `POST /imports/assignments/execute` 和资产嵌套 Payload 路径，文档存在但运行时未匹配 `POST /touchpoint-payloads`。该差异记录为契约风险，不在本次修改 API 或代码。
- Core 与 `card-switch-demo` 为独立外部平台/演示项目，不计入银行后台 M1～M5 完成度。Core 的无认证、可选 `userId`、默认 CORS `*`、Webhook Secret 读取风险以及 analytics 滚动窗口限制继续作为外部安全和发布风险。
- 当前 7 个阻塞任务 `X-WORK-003`、`T-PERF-001`、`R-P3-007`、`R-P5-001`、`R-P5-004`、`R-P5-008`、`R-P5-010` 均保留 `阻塞待确认`；`P1-ENV-004` 已完成真实 Docker 隔离环境验收；`X-ANL-004` 已按范围决议延期至 V1.4，不再计入当前阻塞数。详细负责人、依赖、证据文件、执行入口和关闭条件已写入[详细开发任务清单](./development-task-checklist.md)；完成前 V1.3.2 不得生产发布。

## Epic/Issue/任务索引

本索引是任务治理入口，不复制单项任务状态，也不构成阻塞收敛矩阵。任务状态、负责人、依赖、产出物和验收条件仍以[详细开发任务清单](./development-task-checklist.md)为准。

- Issue #7：承载 V1.3.2 当前任务，包括 API、M1～M5、横向能力、前端、测试、环境和发布门禁；当前仍为内部开发/测试基线，不因索引建立而关闭外部阻塞。
- Issue #9：承载 Casdoor 真实认证与权限延期任务 `P0-CAS-001～006`、`DEC-CAS-001～006`，目标版本 V1.4。
- Issue #10：承载 NFC 真机、硬件和 SDK 延期任务 `P0-NFC-001～002`、`DEC-NFC-001～002`，目标版本 V1.4。

| Epic ID | Issue | 任务 ID/范围 | 主负责人 | 前置依赖 | 阶段验收文档 | 版本边界 |
| --- | --- | --- | --- | --- | --- | --- |
| `EPIC-CHARTER-001` | #7 | `P0-BASE-001` | 架构师 | 关联任务依赖列 | `project-charter.md` | V1.3.2 |
| `EPIC-P0-001` | #7 | `R-P3-001` | 产品/架构 | 关联任务依赖列 | `master-checklist.md` | V1.3.2 |
| `EPIC-P1-001` | #7 | `R-P3-001` | 产品/架构 | 关联任务依赖列 | `master-checklist.md` | V1.3.2 |
| `EPIC-API-001` | #7 | `DEC-IDEMP-001`、`DEC-ANL-001`、`F-COM-004` | API/后端 | 关联任务依赖列 | `../03-api/openapi.yaml`、`../08-testing/acceptance-matrix.md` | V1.3.2 |
| `EPIC-API-002` | #7 | `T-SEC-002` | API/安全 | 关联任务依赖列 | `../05-security/permission-matrix.md` | V1.3.2 |
| `EPIC-DATA-001` | #7 | `P0-DB-002`、`DEC-DATA-001`、`DEC-DATA-002` | 架构/DBA | 关联任务依赖列 | `../04-database/data-dictionary.md` | V1.3.2 |
| `EPIC-SEC-001` | #7；Casdoor 子集→#9 | `P0-CAS-005`、`DEC-CAS-005` | 安全/平台 | 关联任务依赖列 | `../05-security/permission-matrix.md` | V1.3.2；Casdoor V1.4 |
| `EPIC-SCHEMA-001` | #7 | `T-UNIT-001` | 后端/测试 | 关联任务依赖列 | `../08-testing/test-strategy.md` | V1.3.2 |
| `EPIC-REF-001` | #7 | `T-API-001` | 后端/测试 | 关联任务依赖列 | `../08-testing/acceptance-matrix.md` | V1.3.2 |
| `EPIC-A-M2-001` | #7 | `X-IMP-003`、`T-UNIT-002` | 后端/M2 | 关联任务依赖列 | `../01-product/business-rules.md` | V1.3.2 |
| `EPIC-A-M3-001` | #7 | `X-IMP-003`、`T-UNIT-002`、`R-P3-004` | 后端/M3 | 关联任务依赖列 | `../03-api/openapi.yaml` | V1.3.2；NFC 真机 V1.4 |
| `EPIC-B-M4-001` | #7 | `T-UNIT-002` | 后端/M4 | 关联任务依赖列 | `../01-product/state-machines.md` | V1.3.2 |
| `EPIC-B-M5-001` | #7 | `T-UNIT-002`、`R-P3-004` | 后端/M5 | 关联任务依赖列 | `../03-api/openapi.yaml`、`../08-testing/acceptance-matrix.md` | V1.3.2 |
| `EPIC-IMP-001` | #7 | `DEC-IMP-001` | 产品/后端 | 关联任务依赖列 | `../03-api/openapi.yaml` | V1.3.2；异步执行 V1.4 |
| `EPIC-X-IMP-001` | #7 | `R-P3-004` | 后端/运维 | 关联任务依赖列 | `../09-deployment/release-process.md` | V1.3.2；异步执行 V1.4 |
| `EPIC-EXP-001` | #7 | `DEC-EXP-001` | 产品/安全 | 关联任务依赖列 | `../03-api/openapi.yaml` | V1.3.2 |
| `EPIC-X-EXP-001` | #7 | `R-P3-004` | 后端/运维 | 关联任务依赖列 | `../09-deployment/release-process.md` | V1.3.2；异步导出 V1.4 |
| `EPIC-FRONTEND-001` | #7 | `F-COM-006`、`F-M1-001`、`F-M1-002`、`F-M2-001`、`F-M2-002`、`F-M3-001`、`F-M3-002`、`F-M4-001`、`F-M5-001`、`F-EXP-001`、`F-E2E-001`、`F-PERF-001`、`T-FE-001`、`T-FE-002` | 前端 | 关联任务依赖列 | `../08-testing/acceptance-matrix.md` | V1.3.2；真实 Casdoor/NFC V1.4 |
| `EPIC-RELEASE-001` | #7 | `DEC-PERF-001`、`DEC-REL-001` | 运维/发布 | 关联任务依赖列 | `../09-deployment/release-process.md`、`../09-deployment/rollback.md` | V1.3.2 |
| `EPIC-M2-001` | #7 | `DEC-M4-001` | 产品/M2 | 关联任务依赖列 | `../01-product/business-rules.md` | V1.3.2 |
| `EPIC-M4-001` | #7 | `DEC-M4-004` | 产品/M4 | 关联任务依赖列 | `../01-product/state-machines.md` | V1.3.2；预约绑定 V1.4 |

## P0：开发前必须完成

- [x] 确认银行后台与 LinkForty Core 边界
- [x] 确认 Python 后端和前端真实代码目录：`bank-touchpoint-backend/`、`bank-touchpoint-frontend/`；后端已有局部 M1～M5 代码落点，前端 M1～M5 当前仍为工程骨架
- [x] 确认 MVP 范围和不纳入项
- [x] 确认 M1～M5 负责人以及工作包 A、B 的主负责人
- [ ] 完成 Casdoor 真实环境 PoC，并确认 `employee_code` Claim（延期至 V1.4；V1.3.2 保留开发/测试 Mock）
- [x] 完成 LinkForty API PoC
- [x] 获取并验证真实 Webhook 样例（本地真实投递、验证和负责人正式确认已完成）
- [x] 确认 NFC/NDEF Mock 方案（真实设备、SDK、写卡和读回核验延期至 V1.4）
- [ ] 确认 PostgreSQL、Redis 和环境访问权限（本地容器健康；迁移 revision、银行后台/Worker 和生产访问证据待补）
- [ ] 确认银行数据库迁移/运行角色权限（本地单账号配置可用于测试；LinkForty 数据库只读账号延期至 V1.4）
- [ ] 冻结 V1.3.2 物理模型、V3.1 模块方案、权限矩阵、API 规范、7 张表数据字典和状态机（见 [V1.3.2-FREEZE-001](./v1.3.2-freeze-001.md)；外部证据门禁未闭合）
- [x] 配置 Git 分支保护、PR 模板和 CI 基础检查
- [x] 在现有 Issue #7、#9、#10 中关联[详细开发任务清单](./development-task-checklist.md)中的任务 ID；保留已明确的阻塞和延期状态，不把它们误标为完成
- [x] 使用现有 Issue #7、#9、#10 维护目标、范围、验收、负责人、依赖、风险和回滚方案；不为子任务新建 Issue
- [x] 建立 Epic/Issue/任务治理索引并接入自动校验
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

- [ ] 工作包 A：M1～M3 基础能力、主数据和触点资产闭环
- [ ] 工作包 B：M4～M5 绑定生命周期和访问事件运营闭环
- [ ] 按[详细开发任务清单](./development-task-checklist.md)逐项推进模块和横向能力任务，不以本清单替代单项验收标准
- [ ] 非编号统计与报表能力完成 M5 和 LinkForty API-only 数据联调；Core 未提供的指标不得以数据库直连补齐
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
| 银行后台 Python/React 工程目录及实现状态 | 待指定 | 2026-08-19 | 已确认目录；后端局部代码已落地，前端 M1～M5 仍为骨架，完整业务闭环待开发 |
| Casdoor issuer/audience/JWKS/employee_code Claim | 平台/安全 | V1.4 | 延期至 V1.4；真实外部证据待补 |
| LinkForty API 契约 | LinkForty 负责人 | 待指定 | 本地创建/查询和健康检查可用；同 Key 重复请求产生两个 Link，作为 V1.3.2 已知风险；安装/App 聚合统计本版本不纳入，正式字段、TLS/ACL 和只读证据按对应版本边界处理 |
| Webhook 签名和事件样例 | LinkForty 负责人 | 待指定 | 本地真实样例已验证；负责人正式确认已完成 |
| NFC 设备和 NDEF 方案 | 硬件/业务 | V1.4 | 延期至 V1.4；真实外部证据待补，V1.3.2 使用 Mock |
| 数据库部署和只读账号 | 数据库/运维 | 待指定 | 代码 head 为 Alembic `0004_payload_target_url`；本次未连接 PostgreSQL/Redis/Celery，Worker、迁移、运行权限和生产证据待确认；LinkForty 数据库只读账号延期至 V1.4，V1.3.2 统计只调用 API |
