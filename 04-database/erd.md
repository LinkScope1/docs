# V1.3.2 数据关系与逻辑外键规则

## 1. 数据关系图

~~~mermaid
erDiagram
  organization_units ||--o{ employees : owns
  organization_units ||--o{ touchpoint_assets : scopes
  employees ||--o{ touchpoint_assets : responsible_for
  touchpoint_assets ||--o{ touchpoint_payloads : has
  organization_units ||--o{ touchpoint_address_pages : owns
  touchpoint_address_pages ||--o{ touchpoint_payloads : selected_by
  touchpoint_assets ||--o{ touchpoint_employee_assignments : assigned
  employees ||--o{ touchpoint_employee_assignments : receives
  organization_units ||--o{ touchpoint_employee_assignments : scopes
  touchpoint_assets ||--o{ access_events : references
  touchpoint_employee_assignments ||--o{ access_events : resolves
  employees ||--o{ operation_logs : operates
  organization_units ||--o{ operation_logs : scopes
~~~

V1.3.2 的银行业务关系均为应用层逻辑外键，不创建数据库 FOREIGN KEY，也不使用级联删除。组织层级通过 organization_units.org_code 前缀解析，不保存 parent_org_id。

## 2. 通用校验规则

- 所有本地逻辑外键使用与目标主键一致的 BIGINT，LinkForty 外部逻辑引用使用 UUID。
- Router 不接受由调用方绕过业务规则写入责任范围字段；Service 根据访问上下文和目标对象计算或校验责任范围。
- 非空逻辑外键在写入前必须验证目标存在；需要参与当前业务的组织、员工、资产和内容还必须满足对应启用状态。
- 历史记录允许继续引用已停用主数据，但不得引用不存在或已被物理删除的主数据。
- MVP 业务 API 不提供组织、员工、资产、内容、绑定、事件和操作日志的物理删除；通过停用、作废、解绑或归档保留历史。
- 运维清理属于受控维护操作，必须先检查全部逻辑引用、备份和审计，不得通过业务 Repository 静默删除。
- 逻辑外键校验不能替代数据库唯一约束、排他约束和事务锁；并发冲突以数据库约束为最终防线。

## 3. 本地逻辑外键清单

| 本表字段 | 目标字段 | 可空 | 写入和状态校验 | 目标停用后的处理 | 删除校验 |
| --- | --- | ---: | --- | --- | --- |
| organization_units.created_by_employee_id | employees.id | 是 | 人工创建时取当前启用员工；系统初始化可空 | 保留历史引用 | 员工存在审计引用时不得物理删除 |
| organization_units.updated_by_employee_id | employees.id | 是 | 人工修改时取当前启用员工 | 保留历史引用 | 员工存在审计引用时不得物理删除 |
| employees.org_id | organization_units.id | 否 | 创建、调动或重新启用员工时组织必须存在且启用 | 已有员工保留；停用组织前必须处理启用员工 | 存在员工时组织不得物理删除 |
| employees.created_by_employee_id | employees.id | 是 | 人工创建时取当前启用员工；初始化可空 | 保留历史引用 | 被引用员工不得物理删除 |
| employees.updated_by_employee_id | employees.id | 是 | 人工修改时取当前启用员工 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_assets.org_id | organization_units.id | 否 | 创建、调拨或启用资产时组织必须存在且启用 | 已有资产保留；停用组织前必须处理非作废资产 | 存在资产时组织不得物理删除 |
| touchpoint_assets.employee_id | employees.id | 是 | 非空时员工必须存在且启用，且资产 org_id 等于员工 org_id | 员工停用前必须先解绑或转交当前责任资产 | 存在当前责任引用时员工不得物理删除 |
| touchpoint_assets.created_by_employee_id | employees.id | 是 | 人工创建时取当前启用员工；导入或系统任务可空 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_assets.updated_by_employee_id | employees.id | 是 | 人工修改时取当前启用员工 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_payloads.asset_id | touchpoint_assets.id | 否 | 资产必须存在且未永久作废 | 资产停用时内容保留，是否可用由内容状态共同决定 | 存在内容时资产不得物理删除 |
| touchpoint_address_pages.org_id | organization_units.id | 否 | 地址页面创建或修改责任组织时必须存在、启用且在操作者范围内 | 停用后保留页面和既有 Payload 关联；目标配置变化按 Core 补偿传播 | 被 Payload 使用时不得物理删除 |
| touchpoint_payloads.address_page_id | touchpoint_address_pages.id | 是 | 选择时页面必须存在、启用、可读，且责任组织是资产组织的祖先或同组织 | 停用不删除历史关联；目标变化更新同一 Core Link 和 Payload `target_url` 快照，`payload_value` 不变 | 被引用地址页面不得物理删除 |
| touchpoint_payloads.org_id | organization_units.id | 否 | 由所属资产同步，禁止客户端独立指定 | 随资产责任范围调整 | 存在内容时组织不得物理删除 |
| touchpoint_payloads.employee_id | employees.id | 是 | 由所属资产同步，禁止客户端独立指定 | 随资产绑定、解绑或转交同步 | 被引用员工不得物理删除 |
| touchpoint_payloads.created_by_employee_id | employees.id | 是 | 人工创建时取当前启用员工；系统任务可空 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_payloads.updated_by_employee_id | employees.id | 是 | 人工修改时取当前启用员工 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_employee_assignments.asset_id | touchpoint_assets.id | 否 | 资产必须存在且未永久作废；绑定区间不得重叠 | 资产停用或作废不删除历史绑定 | 存在绑定历史时资产不得物理删除 |
| touchpoint_employee_assignments.org_id | organization_units.id | 否 | 取绑定员工的直接所属组织，且与绑定后资产 org_id 一致 | 作为绑定责任范围保留 | 存在绑定历史时组织不得物理删除 |
| touchpoint_employee_assignments.employee_id | employees.id | 否 | 新建绑定时员工必须存在且启用 | 员工停用前必须先结束当前绑定；历史绑定保留 | 存在绑定历史时员工不得物理删除 |
| touchpoint_employee_assignments.created_by_employee_id | employees.id | 是 | 人工绑定时取当前启用员工；系统任务可空 | 保留历史引用 | 被引用员工不得物理删除 |
| touchpoint_employee_assignments.updated_by_employee_id | employees.id | 是 | 解绑或补充原因时取当前启用员工 | 保留历史引用 | 被引用员工不得物理删除 |
| access_events.asset_id | touchpoint_assets.id | 否 | 写入银行事件投影前必须先解析到本地资产 | 事件事实保留，不随资产停用或作废删除 | 存在事件时资产不得物理删除 |
| access_events.binding_id | touchpoint_employee_assignments.id | 是 | 命中事件时间内绑定时写入；未命中可空 | 保留事件发生时的绑定引用 | 存在事件时绑定不得物理删除 |
| access_events.org_id | organization_units.id | 是 | 从事件时命中的资产和绑定解析，待关联时可空 | 事件事实保留 | 存在事件时组织不得物理删除 |
| access_events.employee_id | employees.id | 是 | 从事件时命中的绑定解析，待关联时可空 | 事件事实保留 | 存在事件时员工不得物理删除 |
| operation_logs.org_id | organization_units.id | 是 | 有明确数据范围时写入；系统级任务可空 | 审计事实永久保留 | 存在审计记录时组织不得物理删除 |
| operation_logs.employee_id | employees.id | 是 | 人工操作写当前员工；系统任务可空 | 审计事实永久保留 | 存在审计记录时员工不得物理删除 |

所有业务表中的 created_by_employee_id、updated_by_employee_id 均使用同一规则：人工操作写当前员工，无法归属到员工的初始化或系统任务可以为空，不因员工停用而清空历史值。

## 4. 多态和外部逻辑引用

| 本表字段 | 逻辑目标 | 规则 |
| --- | --- | --- |
| operation_logs.object_id | 由 object_type 决定的本地业务对象 | 多态引用，不建立单一物理外键；写日志时必须校验类型与对象 ID 匹配 |
| operation_logs.external_object_id | 外部系统对象 | UUID，仅记录必要引用，不跨库校验物理外键 |
| touchpoint_payloads.linkforty_link_id | LinkForty links.id | 通过 LinkForty API 返回值或受限读取核验；不直接修改 LinkForty 表 |
| access_events.click_id | LinkForty click_events.id | UUID 普通逻辑引用，允许多个 event_id 引用同一 click_id |

## 5. 组织、员工和责任范围一致性

- 员工只属于一个直接组织，employees.org_id 是员工责任范围根。
- 资产绑定员工后，touchpoint_assets.employee_id 等于当前绑定员工，touchpoint_assets.org_id 等于该员工的 org_id。
- 载体内容的 org_id、employee_id 必须与所属资产一致，由 M3 Service 同步维护。
- 地址页面的 `org_id` 是责任组织；`content_type` 为 1 小程序、2 APP、3 网页；`url` 只做首尾空格清理。网页/小程序 `target_url` 是直接 Core 目标，小程序必须为公开 HTTPS Universal Link；APP 由 `metadata` 解析为 `app-open.html` Bridge。Payload 通过可空 `address_page_id` 逻辑关联，并保存实际 Core 目标快照。
- M4 绑定、解绑和转交必须在同一事务内更新绑定记录、资产责任范围和全部所属内容责任范围。
- 前端传入的组织或员工 ID 只能缩小查询条件，不能扩大访问上下文的数据范围。

## 6. 删除和停用规则

- MVP 业务接口不提供物理删除，组织和员工使用停用，资产使用停用或永久作废，内容使用停用或失效，绑定使用解绑。
- 地址页面使用停用/启用；停用不影响既有 Payload、历史查询、审计记录或已经写入 NFC 的内容。目标配置变化会传播到现有短链，失败时补偿 Core；展示字段变化不传播。
- 停用组织前必须确认不存在启用的下级组织、启用员工、非作废资产和当前有效绑定。
- 停用员工前必须先结束或转交当前有效绑定，并清除资产和内容中的当前员工责任引用。
- 永久作废资产前必须结束当前有效绑定；内容、绑定、事件和操作日志继续保留。
- operation_logs 禁止更新和删除；事件和绑定历史不得因主数据状态变化被级联删除。
- 任何受控物理清理必须由单独的运维方案说明范围、备份、引用检查和审计，不属于普通业务 API。

V1.3.2 不包含 iam_*、target_resources 或 routing_rules。
