# ADR-004：M3 可复用地址页面主数据

## 状态

Accepted（2026-09-14，代码增量已落地，真实数据库迁移验收待补）

## 背景

载体内容管理需要让操作人员按资产权限选择可复用的地址页面。该能力属于 M3
主数据，不应把银行地址页面误建模为 `target_resources` 或 `routing_rules`。
小程序、APP 和网页的实际内容也不能被错误地限制为 HTTP/HTTPS URL。

## 决策

- 新增银行侧 `bank_admin.touchpoint_address_pages`，以 `address_code` 作为全局业务唯一键。
- 页面保存责任 `org_id`、`address_name`、`content_type`（1 小程序、2 APP、3 网页）、`url`、`target_url` 和 `status`；`url` 和页面目标只校验非空与长度，不做通用 URL scheme 审查。
- `touchpoint_payloads` 增加可空 `address_page_id`；选择页面时由 Service 从数据库读取目标配置，并写入 Payload 的实际 Core `target_url` 快照，`payload_value` 始终保持 NFC 卡内内容。新建选择页面时由后端通过 LinkForty API 创建 Link 并以返回短链作为 `payload_value`，客户端不得提交 Link ID。
- 页面责任组织采用 Service 层逻辑范围校验，不建立数据库级外键；根组织页面可供下级资产使用，下级组织页面不得跨组织使用。
- 页面不提供物理删除；停用不重写既有 Payload、NFC 内容或 LinkForty 状态。目标配置变化先提交页面主数据和审计，提交后创建 `touchpoint_address_page_reapply_jobs` 任务，由 Worker 通过统一应用 Service 更新同一个 LinkForty Link；展示名称、说明和无关元数据变化不创建任务。
- 网页和小程序直接将目标提交给 LinkForty Core；小程序要求公开 HTTPS Universal Link。APP 严格复用 `card-switch-demo` 的 `app-open.html` Bridge URL，使用 `metadata.app` 生成按 Link ID 区分的目标。
- Core 与银行数据库无法形成单一事务；流程先预读外部目标快照，事务外更新 Core，再用第二笔短事务重新校验页面版本、Payload 关系和组织范围后写银行库，银行落库失败或任务明细失败时按旧目标补偿。目标切换不重新写 NFC。
- 地址页面普通创建由服务端按内容类型生成 `address_code`；导入更新沿用 `address_code` 匹配，新增行可留空并自动生成；缺失 CSV 行不触发停用、归档或删除。

## 影响

- 当前 Alembic `0006_touchpoint_address_pages` 已创建地址页面表并为 `touchpoint_payloads.address_page_id` 建立索引；本次新增 `0009_address_page_reapply_jobs` 创建任务和明细表。应用启动不自动改表，部署流程须显式执行 `alembic upgrade head`。
- 新增地址页面 API、权限、操作审计对象类型、导入模板、标准导出和前端管理页面。
- 地址页面被停用后仍可作为历史 Payload 的逻辑引用；新的下拉选项只返回启用且可用于目标资产的页面。

## 验收和风险

- Schema、模型、OpenAPI、前端类型检查、Ruff、mypy 和针对性测试已执行；真实 PostgreSQL、Core 和浏览器端到端传播仍需环境验收。
- 本次未连接真实 PostgreSQL，因此 migration upgrade/downgrade、索引实库状态和生产权限仍需 DBA 环境验收。
- 现有冻结记录 `V1.3.2-FREEZE-001` 保留其历史快照；本 ADR 与 `CHG-007` 作为本次 M3 增量的决策和影响记录。
