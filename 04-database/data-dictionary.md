# V1.3.2 数据物理模型与数据字典

> **主版本来源**：本 Markdown 文件；[原始 DOCX](../archive/baselines/physical-model/v1.3.2.docx) 仅作只读归档。
> **逻辑关系**：逻辑外键、引用校验和删除规则以 [V1.3.2 数据关系与逻辑外键规则](./erd.md) 为准。
> **状态转换**：各状态字段的允许转换、前置条件和终态规则以 [V1.3.2 状态转换规则](./state-machines.md) 为准。

> 版本定位：V1.3.2 正式模型：8 张银行业务表 + 1 张批量导入任务表 + 8 张 LinkForty 外部现有表 + Casdoor 外部身份边界。

| 项目 | 内容 |
| --- | --- |
| 文档名称 | 银行触点载体管理系统数据物理模型 |
| 版本 | V1.3.2 |
| 编制日期 | 2026-08-19 |
| 银行后台数据库 | PostgreSQL 14+ |
| 业务服务 | Python 3.11+ / FastAPI / SQLAlchemy 2.x / Alembic |
| 认证平台 | Casdoor（外部身份、角色与功能权限） |
| 外部触点平台 | LinkForty（通过 API / 受限读取交互） |

## 设计结论

V1.3.2 将组织层级、员工责任范围、NFC 载体、载体实际内容、员工绑定、访问事件和员工操作审计纳入银行后台物理模型。

# 1. 模型范围与系统边界

本版本物理模型面向银行触点载体管理后台，覆盖组织、员工、NFC 触点载体、可复用地址页面、卡内内容、员工绑定生命周期、访问事件接入和员工操作审计。Casdoor 负责身份认证、角色和功能权限；银行后台根据本地员工主数据和业务表中的责任范围字段执行数据过滤。

> 边界原则：银行库只维护银行业务主数据和审计投影；LinkForty 的物理表不由银行系统直接执行 DDL、DML、TRUNCATE 或迁移。

## 1.1 V1.3.2 数据域职责

| 数据域 | 物理模型 | 职责 |
| --- | --- | --- |
| 组织 | organization_units | 以 org_code 前缀表达组织层级和数据范围根节点 |
| 员工 | employees | 维护员工编码、员工名称和直接所属组织 |
| 触点资产 | touchpoint_assets | 维护 NFC 载体业务编码、物理 UID 和当前责任 |
| 地址页面 | touchpoint_address_pages | 维护可复用地址页面、责任组织、内容类型、展示值、实际内容和状态 |
| 载体内容 | touchpoint_payloads | 记录卡内实际写入内容及 LinkForty 逻辑引用；不持久化专属外部同步状态 |
| 员工绑定 | touchpoint_employee_assignments | 追加保存载体与员工的当前及历史绑定 |
| 访问事件 | access_events | 接收事件幂等投影并关联资产、组织和员工 |
| 操作审计 | operation_logs | 记录员工和系统操作，不保存敏感凭证 |
| 批量导入任务 | import_batches | 持久化异步导入状态、幂等键和安全结果；不属于 M1～M5 业务主数据 |
| 外部系统 | Casdoor / LinkForty | 身份、角色、链接和访问底层能力，不属于银行业务表 |

## 1.2 V1.3.2 下线对象

- 删除全部本地 iam_* 表；Casdoor 是身份、角色和功能权限的权威来源。

- 删除 target_resources；载体内容不再依赖目标资源对象。

- 删除 routing_rules；旧 M5 目标资源管理、旧 M6 路由规则配置和发布流程不属于本版本。

- LinkForty 仍保留链接、点击和 Webhook 能力，但不再承载银行后台路由规则发布职责。

# 2. 公共物理设计规范

## 2.1 标识、时间和 JSON 字段

- 本系统主键使用 BIGINT 雪花 ID，API 层按字符串传输；LinkForty 外部对象继续使用 UUID。

- 时间统一使用带时区的 TIMESTAMPTZ；LinkForty 原有表的时间类型按外部模型保留。

- JSONB 只承载低频、结构可能变化的扩展属性；核心查询字段必须显式建模。

- 银行业务表不建立数据库级级联删除；具体逻辑外键、引用完整性和删除前检查统一见 [数据关系与逻辑外键规则](./erd.md)。

## 2.2 组织编码层级

- 根组织编码为 1，每级下级组织在父组织编码后追加三位数字，例如 1 → 1001 → 1001001。

- 组织编码满足 ^1([0-9]{3})*$，全局唯一；直接下级必须是父编码追加恰好三位数字。

- 祖先和下级组织通过前缀查询，不保存 parent_org_id，不新增 org_level。

- 服务端负责校验编码格式、前缀关系和重复编码；数据库负责格式检查和唯一约束。

## 2.3 数据责任范围

- org_id 表示本条数据的数据责任组织；employee_id 表示当前直接责任员工。

- 员工表只保存直接所属 org_id；employees.id 本身就是员工 ID，不重复增加 employee_id。

- 库存资产、公共数据或系统生成事件可以将 employee_id 置空，但不能绕过 org_id 责任校验。

- 前端传入的员工 ID 或组织 ID 不能扩大后端查询、导出和导入权限。

## 2.4 幂等、唯一性和审计

- asset_code、employee_code、org_code 和 event_id 全局唯一；非空 carrier_uid 唯一。

- click_id 仅作为 LinkForty 点击逻辑引用，允许重复，不设置唯一约束。

- 同一资产的有效员工绑定时间区间不得重叠；新绑定必须新增记录，解绑只结束当前有效记录，不删除或覆盖历史记录。

- operation_logs 只追加；写接口、Webhook、批处理、外部同步和导入均须有明确幂等策略。

## 2.5 V1.3.2 冻结约束对照

以下约束是 `V1.3.2-FREEZE-001` 的数据库验收基线，迁移必须逐项落地；已应用迁移不得回改，修正只能新增 Alembic revision。

| 约束域 | 冻结值 |
| --- | --- |
| 表数量 | 银行库固定 8 张业务表 + 1 张横向批量导入任务表：`organization_units`、`employees`、`touchpoint_assets`、`touchpoint_address_pages`、`touchpoint_payloads`、`touchpoint_employee_assignments`、`access_events`、`operation_logs`、`import_batches`。 |
| 外键与删除 | 不建立本地数据库外键，不使用数据库级级联删除；逻辑引用由 Service 校验并保留历史语义。 |
| 枚举 | 组织/员工状态为 `0/1`；资产类型固定 `1=NFC`，资产状态为 `0/1/2/9`；地址页面 `content_type` 为 `1=小程序/2=APP/3=网页`、`status` 为 `0/1`；Payload 类型为 `1/2/3/99`、来源为 `1/2/3/4`、提供方为 `1/2/3/99`、状态为 `0/1/2/3`；绑定状态为 `1/2`；访问关联状态为 `0/1/2/3`；操作结果为 `1/2/3`。 |
| 标识唯一性 | `asset_code`、`employee_code`、`org_code`、`event_id` 全局唯一；非空 `carrier_uid` 唯一；非空 `linkforty_link_id` 全局唯一；`click_id` 不唯一。 |
| 绑定一致性 | 当前绑定 `assignment_status=1` 必须 `effective_to IS NULL`；已解绑记录必须有 `effective_to > effective_from` 和 `unbind_reason_type`；时间区间使用 PostgreSQL 排他约束防重叠。 |
| 事件语义 | `access_events.asset_id` 非空；无法唯一解析本地资产时拒绝写入事件表，只保留安全审计和补偿记录。 |
| 审计 | `operation_logs` 只追加，禁止 UPDATE/DELETE；不得保存 Token、JWT、密码、Webhook Secret 或未脱敏个人信息。 |

# 3. 本系统表清单

| 序号 | 表名 | 归属模块 | 用途 |
| --- | --- | --- | --- |
| 1 | organization_units | M2 | 使用组织编码前缀表示层级的组织表 |
| 2 | employees | M2 | 员工主数据和组织归属 |
| 3 | touchpoint_assets | M3 | NFC 触点载体 |
| 4 | touchpoint_payloads | M3 | 载体实际写入内容 |
| 5 | touchpoint_employee_assignments | M4 | 载体与员工的当前及历史绑定 |
| 6 | touchpoint_address_pages | M3 | 可复用地址页面主数据 |
| 7 | access_events | M5 | Webhook 访问事件投影和关联结果 |
| 8 | operation_logs | M1 | 员工和系统操作审计 |
| 9 | import_batches | 横向能力 | 批量导入幂等批次、异步状态和安全失败报告 |

> 删除范围：V1.3.2 不创建 iam_*、target_resources 或 routing_rules 表；这些对象只在更新日志中作为 V1.2 下线内容保留。`import_batches` 仅存储批处理状态和安全结果，不替代业务表。

# 4. 本系统 8 张表详细定义

## 4.1 organization_units

组织表不使用 parent_org_id，组织层级由 org_code 前缀表达。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| org_code | VARCHAR(64) | 否 | — | 全局唯一；匹配 `^1([0-9]{3})*$` |
| org_name | VARCHAR(128) | 否 | — | 组织名称 |
| status | SMALLINT | 否 | 1 | 0 停用 / 1 启用 |
| sort_no | INTEGER | 否 | 100 | 同级显示顺序 |
| location_code | VARCHAR(64) | 是 | — | 组织区位码 |
| door_no | VARCHAR(32) | 是 | — | 组织门牌号 |
| contact_name | VARCHAR(100) | 是 | — | 联系人 |
| contact_phone_cipher | VARCHAR(256) | 是 | — | 联系人手机号密文 |
| contact_phone_masked | VARCHAR(32) | 是 | — | 联系人手机号脱敏值 |
| description | VARCHAR(500) | 是 | — | 组织说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工逻辑引用 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工逻辑引用 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

> 编码约束：直接子级由应用校验为父编码追加恰好三位数字；下级查询使用组织编码前缀。

## 4.2 employees

原 customer_managers 改为员工表；Casdoor employee_code Claim 用于定位本地员工。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK，同时是员工 ID |
| employee_code | VARCHAR(64) | 否 | — | 全局唯一，必须与 Casdoor Claim 契约一致 |
| employee_name | VARCHAR(100) | 否 | — | 员工姓名 |
| org_id | BIGINT | 否 | — | 直接所属组织逻辑引用 |
| phone_cipher | VARCHAR(256) | 是 | — | 手机号密文 |
| phone_masked | VARCHAR(32) | 是 | — | 手机号脱敏值 |
| status | SMALLINT | 否 | 1 | 0 停用 / 1 正常 |
| description | VARCHAR(500) | 是 | — | 说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

> 认证映射：后端验证 JWT 签名、issuer、audience 和过期时间后读取 employee_code；员工不存在或未启用时拒绝访问。

## 4.3 touchpoint_assets

asset_code 用于业务查询和导入，carrier_uid 用于 NFC 物理盘点，两者不能互相替代。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_code | VARCHAR(64) | 否 | — | 载体业务编码，唯一 |
| asset_type | SMALLINT | 否 | 1 | 1 NFC；一期固定使用 NFC |
| carrier_uid | VARCHAR(128) | 是 | — | NFC 物理 UID；非空时唯一 |
| org_id | BIGINT | 否 | — | 当前数据责任组织 |
| employee_id | BIGINT | 是 | — | 当前直接责任员工；库存时可空 |
| asset_status | SMALLINT | 否 | 0 | 0 库存 / 1 启用 / 2 停用 / 9 永久作废 |
| supplier_code | VARCHAR(64) | 是 | — | 供应商编码 |
| supplier_batch_no | VARCHAR(64) | 是 | — | 供应商批次 |
| metadata | JSONB | 否 | {} | 载体扩展属性对象 |
| description | VARCHAR(500) | 是 | — | 说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

## 4.4 touchpoint_payloads

记录卡内实际写入内容；org_id 和 employee_id 从所属资产同步维护。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_id | BIGINT | 否 | — | 所属载体逻辑引用 |
| org_id | BIGINT | 否 | — | 从载体同步的数据责任组织 |
| employee_id | BIGINT | 是 | — | 从载体同步的直接责任员工 |
| payload_type | SMALLINT | 否 | 1 | 1 短链 / 2 URL / 3 文本 / 99 其他 |
| payload_value | VARCHAR(2048) | 否 | — | 卡内实际写入内容，不是最终目标 |
| address_page_id | BIGINT | 是 | — | 可复用地址页面逻辑引用；选择时由 Service 校验启用状态和组织范围 |
| target_url | VARCHAR(2048) | 是 | — | 关联地址页面的实际目标内容快照；手工 URL 类型内容时可由 payload_value 得出；不强制 HTTP/HTTPS |
| payload_source | SMALLINT | 否 | — | 1 供应商预写 / 2 本系统 / 3 外部导入 / 4 人工录入 |
| provider_type | SMALLINT | 否 | 1 | 1 LinkForty / 2 供应商 / 3 无平台 / 99 其他 |
| linkforty_link_id | UUID | 是 | — | LinkForty 链接逻辑引用；非空时全局唯一，一个外部 Link 只能关联一条 Payload |
| status | SMALLINT | 否 | 0 | 0 待登记 / 1 有效 / 2 停用 / 3 失效 |
| metadata | JSONB | 否 | {} | 低频扩展属性对象 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

> 外部同步：linkforty_link_id 仅为 LinkForty 逻辑引用；touchpoint_payloads 不保存 LinkForty 专属同步状态，外部调用结果由 operation_logs 和 trace_id 审计。

## 4.5 touchpoint_address_pages

可复用地址页面主数据。`org_id` 是责任组织；地址页面可供同组织及下级资产使用。
`content_type` 区分小程序、APP 和网页，`target_url` 保存实际内容，不强制要求
HTTP/HTTPS scheme。`url` 保留为管理页面展示值；没有独立目标值时由 Service 使用
`url` 初始化 `target_url`。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK；API 以字符串传输 |
| address_code | VARCHAR(64) | 否 | — | 全局唯一；创建和导入幂等键 |
| address_name | VARCHAR(128) | 否 | — | 页面显示名称/地址标识 |
| url | VARCHAR(2048) | 否 | — | 管理页面展示值；仅校验非空和长度 |
| target_url | VARCHAR(2048) | 否 | — | 实际目标内容；仅校验非空和长度，不审查 HTTP/HTTPS 格式 |
| content_type | SMALLINT | 否 | 3 | 1 小程序 / 2 APP / 3 网页 |
| org_id | BIGINT | 否 | — | 责任组织，逻辑引用 `organization_units.id` |
| status | SMALLINT | 否 | 1 | 0 停用 / 1 启用 |
| description | VARCHAR(500) | 是 | — | 说明 |
| metadata | JSONB | 否 | {} | 扩展属性对象 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

地址页面修改或停用不会自动重写既有 `touchpoint_payloads`，也不会自动改变 NFC
卡内容或 LinkForty 外部状态。被 Payload 使用的地址页面不得物理删除。

## 4.6 touchpoint_employee_assignments

新绑定必须新增记录；解绑通过更新当前有效记录的 `assignment_status`、`effective_to`、解绑操作人和解绑原因结束绑定。绑定历史不得删除、覆盖或恢复，不保存组织、支行和员工名称快照。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_id | BIGINT | 否 | — | 载体逻辑引用 |
| org_id | BIGINT | 否 | — | 绑定记录责任组织 |
| employee_id | BIGINT | 否 | — | 绑定员工 |
| assignment_status | SMALLINT | 否 | 1 | 1 当前有效 / 2 已解绑 |
| effective_from | TIMESTAMPTZ | 否 | NOW() | 生效时间 |
| effective_to | TIMESTAMPTZ | 是 | — | 失效时间 |
| unbind_reason_type | SMALLINT | 是 | — | 解绑原因码 |
| unbind_reason | VARCHAR(500) | 是 | — | 解绑说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 记录时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 最后更新时间 |

> 历史规则：历史查询显示当前员工和组织名称，不保证还原绑定发生时的名称。
> 状态规则：绑定、解绑和转交的完整状态转换与事务要求统一见 [状态转换规则](./state-machines.md#5-m4-绑定状态)。

## 4.7 access_events

事件关联状态只表示资产、组织和员工关联。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| event_id | VARCHAR(255) | 否 | — | Webhook 全局唯一幂等键 |
| click_id | UUID | 否 | — | LinkForty 点击逻辑引用，非唯一 |
| asset_id | BIGINT | 否 | — | 访问载体 |
| binding_id | BIGINT | 是 | — | 事件时命中的绑定记录 |
| org_id | BIGINT | 是 | — | 事件关联组织 |
| employee_id | BIGINT | 是 | — | 事件关联员工 |
| resolution_status | SMALLINT | 否 | 0 | 0 待关联 / 1 成功 / 2 待重试 / 3 失败 |
| resolution_reason | VARCHAR(255) | 是 | — | 关联结果摘要 |
| event_metadata | JSONB | 否 | {} | 低频事件属性对象 |
| resolved_at | TIMESTAMPTZ | 是 | — | 当前关联尝试完成时间 |
| received_at | TIMESTAMPTZ | 否 | NOW() | 首次接收时间，不更新 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 本地写入时间 |

## 4.8 operation_logs

员工和系统操作审计，只追加且不记录密码、Token、密钥或 Secret。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK |
| trace_id | VARCHAR(64) | 否 | — | 请求或批次追踪号 |
| org_id | BIGINT | 是 | — | 本次操作数据范围 |
| employee_id | BIGINT | 是 | — | 操作员工；系统任务可空 |
| operation_type | SMALLINT | 否 | — | 1 登录 / 2 创建 / 3 修改 / 4 启停 / 5 绑定 / 6 解绑 / 7 调拨 / 8 导入 / 9 导出 / 10 外部同步 / 99 其他 |
| object_type | SMALLINT | 否 | — | 1 组织 / 2 员工 / 3 载体 / 4 内容 / 5 绑定 / 6 事件 / 7 导入 / 9 地址页面 / 99 其他 |
| object_id | BIGINT | 是 | — | 本系统对象 ID |
| external_object_id | UUID | 是 | — | 外部对象 ID |
| operation_result | SMALLINT | 否 | — | 1 成功 / 2 失败 / 3 部分成功 |
| operation_summary | VARCHAR(1000) | 是 | — | 摘要 |
| operation_detail | JSONB | 否 | {} | 请求 ID、批次号、影响数量等 |
| before_data | JSONB | 是 | — | 修改前必要字段 |
| after_data | JSONB | 是 | — | 修改后必要字段 |
| error_code | VARCHAR(64) | 是 | — | 错误码 |
| error_message | VARCHAR(500) | 是 | — | 错误摘要 |
| ip_cipher | VARCHAR(256) | 是 | — | 加密 IP |
| ip_hash | VARCHAR(64) | 是 | — | IP 哈希 |
| user_agent | VARCHAR(512) | 是 | — | 客户端 |
| operation_time | TIMESTAMPTZ | 否 | NOW() | 操作时间 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 写入时间 |

## 4.9 import_batches

批量导入任务表属于横向异步能力，不承载卡片、载体内容或员工主数据。大文件入队前保留上传内容；执行完成后清理 `source_content`，仅保留结果摘要和不含原始内容值、完整手机号的失败报告。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
| --- | --- | --- | --- | --- |
| id | BIGINT | 否 | 雪花算法 | PK；API 以字符串传输 |
| template_type | VARCHAR(32) | 否 | — | `asset` / `payload` / `employee` / `address_page` |
| status | VARCHAR(16) | 否 | — | `queued` / `running` / `completed` / `failed` |
| idempotency_key | VARCHAR(128) | 否 | — | 全局唯一；同键重放返回原批次 |
| created_by_employee_id | BIGINT | 否 | — | 创建者；用于批次结果访问控制 |
| org_id | BIGINT | 否 | — | 创建者组织快照 |
| filename | VARCHAR(255) | 是 | — | 原始文件名，不记录文件内容 |
| content_type | VARCHAR(128) | 是 | — | 上传媒体类型 |
| source_content | BYTEA | 是 | — | 待执行文件；完成后清空 |
| total / succeeded / failed | INTEGER | 否 | 0 | 批次统计 |
| result_data | JSONB | 是 | — | 安全行结果，不包含原始内容值或完整手机号 |
| failure_report | BYTEA | 是 | — | UTF-8 BOM CSV 失败报告 |
| created_at / updated_at | TIMESTAMPTZ | 否 | NOW() | 创建和更新时间 |

## 4.10 V1.3.2 数据关系图

参见 [V1.3.2 数据关系图](./erd.md)。V1.3.2 DOCX 中内嵌的图示仍标注为 V1.3.1，不作为 Markdown 主文档内容迁移。

# 5. LinkForty 现有物理模型

LinkForty 的 8 张现有表属于外部系统物理模型，本节仅用于说明银行后台的逻辑引用和数据边界。银行系统通过 API 写入 LinkForty，通过受限读取或 Webhook 获取访问结果，不直接执行其物理表 DDL、DML、TRUNCATE 或迁移。

> 安全边界：Webhook 签名密钥由 LinkForty 管理；本文不展示 `webhooks.secret`，银行系统不通过 LinkForty 数据库直读该字段。受控 Core API provisioning 仅将 Secret 一次性交付为银行后台验签运行时配置，不写入银行业务表或日志。

## 5.1 link_templates

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 模板主键 |
| user_id | UUID | 是 | — | 逻辑外部用户引用 | LinkForty用户标识 |
| name | VARCHAR(255) | 否 | — | — | 模板名称 |
| slug | VARCHAR(100) | 否 | — | UK | 模板唯一标识 |
| description | TEXT | 是 | — | — | 模板说明；保留现有结构 |
| settings | JSONB | 是 | '{}' | — | 模板设置 |
| is_default | BOOLEAN | 是 | FALSE | — | 是否默认模板 |
| created_at | TIMESTAMP | 是 | NOW() | — | 创建时间 |
| updated_at | TIMESTAMP | 是 | NOW() | — | 更新时间 |

## 5.2 links

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 链接主键 |
| user_id | UUID | 是 | — | 逻辑外部用户引用 | LinkForty用户标识 |
| template_id | UUID | 是 | — | 物理FK→link_templates.id | 模板；删除置空 |
| short_code | VARCHAR(20) | 否 | — | UK | 短码 |
| original_url | TEXT | 否 | — | — | 默认原始目标 |
| title | VARCHAR(255) | 是 | — | — | 标题 |
| description | TEXT | 是 | — | — | 说明 |
| ios_app_store_url | TEXT | 是 | — | — | iOS商店地址 |
| android_app_store_url | TEXT | 是 | — | — | Android商店地址 |
| web_fallback_url | TEXT | 是 | — | — | Web回退地址 |
| utm_parameters | JSONB | 是 | '{}' | — | UTM参数 |
| targeting_rules | JSONB | 是 | '{}' | — | 国家、设备、语言定向规则 |
| is_active | BOOLEAN | 是 | TRUE | — | 是否启用 |
| expires_at | TIMESTAMP | 是 | — | — | 过期时间 |
| append_click_id | BOOLEAN | 是 | FALSE | — | 是否向HTTP(S)目标追加lf_click |
| og_title | VARCHAR(255) | 是 | — | — | 社交预览标题 |
| og_description | TEXT | 是 | — | — | 社交预览说明 |
| og_image_url | TEXT | 是 | — | — | 社交预览图片 |
| og_type | VARCHAR(50) | 是 | 'website' | — | OG类型 |
| attribution_window_hours | INTEGER | 是 | 168 | — | 归因窗口小时数 |
| app_scheme | VARCHAR(255) | 是 | — | — | App URI Scheme |
| ios_universal_link | TEXT | 是 | — | — | iOS Universal Link |
| android_app_link | TEXT | 是 | — | — | Android App Link |
| deep_link_path | TEXT | 是 | — | — | App内路径 |
| deep_link_parameters | JSONB | 是 | '{}' | — | 深链参数 |
| created_at | TIMESTAMP | 是 | NOW() | — | 创建时间 |
| updated_at | TIMESTAMP | 是 | NOW() | — | 更新时间 |

## 5.3 click_events

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 点击事件主键 |
| link_id | UUID | 否 | — | 物理FK→links.id | 删除链接时级联 |
| clicked_at | TIMESTAMP | 是 | NOW() | — | 点击时间 |
| ip_address | INET | 是 | — | — | 客户端IP |
| user_agent | TEXT | 是 | — | — | User-Agent |
| device_type | VARCHAR(20) | 是 | — | — | 设备类型 |
| platform | VARCHAR(20) | 是 | — | — | 平台 |
| country_code | CHAR(2) | 是 | — | — | 国家代码 |
| country_name | VARCHAR(100) | 是 | — | — | 国家名称 |
| region | VARCHAR(100) | 是 | — | — | 地区 |
| city | VARCHAR(100) | 是 | — | — | 城市 |
| latitude | DECIMAL(10,8) | 是 | — | — | 纬度 |
| longitude | DECIMAL(11,8) | 是 | — | — | 经度 |
| timezone | VARCHAR(100) | 是 | — | — | 时区 |
| utm_source | VARCHAR(255) | 是 | — | — | UTM来源 |
| utm_medium | VARCHAR(255) | 是 | — | — | UTM媒介 |
| utm_campaign | VARCHAR(255) | 是 | — | — | UTM活动 |
| referrer | TEXT | 是 | — | — | 来源页 |
| is_bot | BOOLEAN | 否 | FALSE | — | 是否机器人 |
| bot_reason | VARCHAR(16) | 是 | — | — | 机器人原因码 |

## 5.4 device_fingerprints

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 指纹主键 |
| click_id | UUID | 否 | — | 物理FK→click_events.id | 删除点击时级联 |
| fingerprint_hash | VARCHAR(64) | 否 | — | — | 指纹哈希 |
| ip_address | INET | 是 | — | — | IP |
| user_agent | TEXT | 是 | — | — | User-Agent |
| timezone | VARCHAR(100) | 是 | — | — | 时区 |
| language | VARCHAR(10) | 是 | — | — | 语言 |
| screen_width | INTEGER | 是 | — | — | 屏幕宽 |
| screen_height | INTEGER | 是 | — | — | 屏幕高 |
| platform | VARCHAR(50) | 是 | — | — | 平台 |
| platform_version | VARCHAR(50) | 是 | — | — | 平台版本 |
| created_at | TIMESTAMP | 是 | NOW() | — | 创建时间 |

## 5.5 install_events

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 安装事件主键 |
| link_id | UUID | 是 | — | 物理FK→links.id | 删除链接时置空 |
| click_id | UUID | 是 | — | 物理FK→click_events.id | 删除点击时置空 |
| fingerprint_hash | VARCHAR(64) | 否 | — | — | 归因指纹 |
| confidence_score | DECIMAL(5,2) | 是 | — | — | 置信度 |
| attribution_method | VARCHAR(20) | 是 | — | — | fingerprint或none |
| matched_factors | TEXT[] | 是 | — | — | 命中因子；保留现有结构 |
| installed_at | TIMESTAMP | 是 | NOW() | — | 安装时间 |
| first_open_at | TIMESTAMP | 是 | — | — | 首开时间 |
| deep_link_retrieved | BOOLEAN | 是 | FALSE | — | 是否已取回深链 |
| deep_link_data | JSONB | 是 | '{}' | — | 深链数据 |
| attribution_window_hours | INTEGER | 是 | 168 | — | 归因窗口 |
| ip_address | INET | 是 | — | — | IP |
| user_agent | TEXT | 是 | — | — | User-Agent |
| timezone | VARCHAR(100) | 是 | — | — | 时区 |
| language | VARCHAR(10) | 是 | — | — | 语言 |
| screen_width | INTEGER | 是 | — | — | 屏幕宽 |
| screen_height | INTEGER | 是 | — | — | 屏幕高 |
| platform | VARCHAR(50) | 是 | — | — | 平台 |
| platform_version | VARCHAR(50) | 是 | — | — | 平台版本 |
| device_id | VARCHAR(255) | 是 | — | — | 可选设备标识 |
| sdk_name | VARCHAR(50) | 是 | — | — | SDK名称 |
| sdk_version | VARCHAR(50) | 是 | — | — | SDK版本 |
| created_at | TIMESTAMP | 是 | NOW() | — | 创建时间 |

## 5.6 in_app_events

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 事件主键 |
| install_id | UUID | 否 | — | 物理FK→install_events.id | 删除安装时级联 |
| event_name | VARCHAR(255) | 否 | — | — | 事件名称 |
| event_data | JSONB | 是 | '{}' | — | 事件属性 |
| event_timestamp | TIMESTAMP | 否 | — | — | 客户端事件时间 |
| attributed_link_id | UUID | 是 | — | 物理FK→links.id | 最后点击归因链接；删除置空 |
| attributed_click_id | UUID | 是 | — | 逻辑引用click_events.id | 原始点击ID；代码未建FK |
| attributed_at | TIMESTAMP | 是 | — | — | 深链打开时间 |
| session_id | UUID | 是 | — | — | App打开会话ID |
| sdk_name | VARCHAR(50) | 是 | — | — | SDK名称 |
| sdk_version | VARCHAR(50) | 是 | — | — | SDK版本 |
| created_at | TIMESTAMP | 是 | NOW() | — | 写入时间 |

## 5.7 webhooks

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | Webhook主键 |
| user_id | UUID | 是 | — | 逻辑外部用户引用 | LinkForty用户标识 |
| name | VARCHAR(255) | 否 | — | — | 订阅名称 |
| url | TEXT | 否 | — | — | 回调URL |
| events | TEXT[] | 否 | '{}' | — | 订阅事件类型 |
| is_active | BOOLEAN | 是 | TRUE | — | 是否启用 |
| retry_count | INTEGER | 是 | 3 | — | 重试次数 |
| timeout_ms | INTEGER | 是 | 10000 | — | 请求超时毫秒 |
| headers | JSONB | 是 | '{}' | — | 附加请求头 |
| created_at | TIMESTAMP | 是 | NOW() | — | 创建时间 |
| updated_at | TIMESTAMP | 是 | NOW() | — | 更新时间 |

> `webhooks.secret` 属于 LinkForty 外部敏感字段，故不在银行侧数据字典字段表、银行业务表或只读字段白名单中展示；受控 API provisioning 不改变该数据库边界。

## 5.8 webhook_deliveries

| 字段 | 类型 | 可空 | 默认值 | 键/引用 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | UUID | 否 | gen_random_uuid() | PK | 投递任务主键 |
| webhook_id | UUID | 否 | — | FK→webhooks.id | 订阅端点，删除级联 |
| event_type | VARCHAR(32) | 否 | — | UK组成部分 | 事件类型 |
| event_id | VARCHAR(255) | 否 | — | UK组成部分 | 业务事件ID |
| payload | JSONB | 否 | — | — | 投递载荷快照 |
| status | VARCHAR(16) | 否 | pending | 普通索引 | pending/processing/delivered/dead_letter |
| attempt_count | INTEGER | 否 | 0 | — | 已尝试次数 |
| next_attempt_at | TIMESTAMP | 否 | NOW() | 普通索引 | 下次重试时间 |
| claimed_at | TIMESTAMP | 是 | — | — | Worker领取时间 |
| last_response_status | INTEGER | 是 | — | — | 最近HTTP状态码 |
| last_response_body | TEXT | 是 | — | — | 最近响应摘要 |
| last_error | TEXT | 是 | — | — | 最近错误摘要 |
| created_at | TIMESTAMP | 否 | NOW() | — | 创建时间 |
| delivered_at | TIMESTAMP | 是 | — | — | 成功时间 |
| dead_lettered_at | TIMESTAMP | 是 | — | — | 死信时间 |

## 5.9 银行后台与 LinkForty 的交互约定

- touchpoint_payloads.linkforty_link_id 逻辑引用 LinkForty.links.id；银行库不复制 LinkForty 链接运行字段。

- LinkForty 的 click_events 或 Webhook 事件通过 event_id、click_id 等逻辑字段进入 access_events。

- touchpoint_payloads 不定义 external_sync_status；M3 负责 LinkForty 调用和外部同步编排，Worker 执行重试与补偿，成功、失败和补偿结果由 M1 通过 operation_logs 与 trace_id 审计。V1.3.2 不再存在 旧 M6 publish_status、version_no 或 last_published_at。

- 目标资源和路由规则不再作为银行后台到 LinkForty 的中间对象。

# 6. 跨系统引用与数据流

V1.3.2 的跨系统数据流以 Casdoor 的身份声明、本地员工主数据、银行载体责任范围和 LinkForty 外部访问能力为边界。

1. 浏览器进入银行后台 BFF；FastAPI 服务端通过 Authorization Code + PKCE 兑换并验证 JWT，浏览器只持有 HttpOnly Session Cookie。

1. 后端从规范化 Claims 获取 employee_code，查询 employees，并拒绝停用或不存在的员工。

1. 查询、导出和导入根据员工所属 org_id 以及本人 employee_id 执行后端数据范围过滤。

1. 触点资产和载体内容通过 LinkForty API 同步；银行业务表只保存 linkforty_link_id 等必要逻辑引用，不持久化 LinkForty 专属同步状态。外部调用结果写入 operation_logs 并保留 trace_id。

1. LinkForty 访问事件通过 event_id、click_id、linkforty_link_id 等字段关联，并写入 access_events。

1. 所有管理操作和批量导入写入 operation_logs；系统任务可将 employee_id 置空但必须保留 trace_id。

> 移除链路：V1.3.2 移除本地 IAM 映射、目标资源解析、路由规则发布以及目标资源到访问事件的关联链路。

# 7. 状态码、枚举与文档导入预留

## 7.1 V1.3.2 状态范围

| 对象 | 状态/类型 | 说明 |
| --- | --- | --- |
| 组织 | status | 0 停用 / 1 启用 |
| 员工 | status | 0 停用 / 1 正常 |
| 资产 | asset_status | 0 库存 / 1 启用 / 2 停用 / 9 永久作废 |
| 载体内容 | status | 0 待登记 / 1 有效 / 2 停用 / 3 失效 |
| 绑定 | assignment_status | 1 当前有效 / 2 已解绑 |
| 访问事件 | resolution_status | 0 待关联 / 1 成功 / 2 待重试 / 3 失败 |
| 操作审计 | operation_type / object_type | 覆盖管理、绑定、同步、导入和导出操作 |

V1.3.2 删除配置状态、目标资源类型、路由冲突和路由发布相关枚举。

## 7.2 文档导入预留方案

- 预留三类模板：载体内容批量修改、载体与员工绑定关系批量修改、载体与载体内容关系批量修改。

- 稳定匹配键：组织使用 org_code，员工使用 employee_code，载体优先使用 asset_code，可辅助 carrier_uid。

- 载体内容使用 asset_code + payload_type 或明确内容记录 ID 作为匹配键。

- 写入策略为更新并新增：匹配到既有记录则更新，匹配不到且必填字段完整则创建。

- 文档缺少某行不推导删除、停用或解绑；解绑和转交必须使用模板显式 `operation` 类型。

- 导入支持预校验、幂等键、逐行校验结果和失败原因；每批导入写入 operation_logs。

- 本版本创建 `import_batches` 批次表承载异步状态、幂等键和安全结果；不创建导入明细表，逐行结果以安全 JSON/失败 CSV 保存。

# 8. Python/FastAPI 与外部系统实施约定

| 层次 | 职责 | 实施约定 |
| --- | --- | --- |
| Router | 协议适配 | 接收请求、解析认证上下文、返回统一响应；不直接写 SQL 或调用外部系统。 |
| Service | 业务规则 | 组织编码校验、数据范围过滤、绑定时间冲突、导入预校验和审计编排。 |
| Repository | 数据库访问 | SQLAlchemy 2.x 查询、事务、索引和约束；不承载 Casdoor 或 LinkForty 业务。 |
| Integration Adapter | 外部调用 | Casdoor OIDC/JWT Claim、LinkForty API、Webhook/NFC 适配和重试。 |
| Worker / Celery | 异步任务 | 外部调用、事件重试、批量导入、补偿和结果审计；不得在银行业务表中补建 LinkForty 专属同步状态字段。 |
| Alembic | 数据库演进 | V1.3.2 通过新迁移创建 8 张银行业务表及横向 `import_batches` 任务表；本次以 `0006_touchpoint_address_pages` 增量创建地址页面并为 Payload 增加逻辑关联；禁止直接删除已部署环境旧表。 |

# 9. V1.3.2 更新日志

| 版本 | 日期 | 变更摘要 |
| --- | --- | --- |
| V1.3 | 2026-08-18 | 银行后台物理模型由 16 张表调整为 7 张表。 |
| V1.3 | 2026-08-18 | customer_managers 重命名为 employees；移除本地 IAM 表及 IAM 引用。 |
| V1.3 | 2026-08-18 | 组织层级改用 org_code 前缀；删除 org_type、parent_org_id、source_type、external_org_id。 |
| V1.3 | 2026-08-18 | 资产保留 asset_code 和 carrier_uid，删除配置状态、位置和门牌字段，增加责任范围字段。 |
| V1.3 | 2026-08-18 | 载体内容、访问事件和操作日志增加员工/组织责任语义。 |
| V1.3 | 2026-08-18 | 绑定历史删除全部名称快照；目标资源和路由规则完整下线。 |
| V1.3 | 2026-08-18 | 新增文档导入预留契约、审计约定和 V1.3 Alembic 建表说明。 |
| V1.3.1 | 2026-08-18 | 取消 external_sync_status 及其枚举；调用结果由 operation_logs 审计。 |
| V1.3.2 | 2026-08-19 | 修正 access_events 模块归属 M7→M5；不改变表数量、字段、状态或外部边界。 |
| V1.3.2 | 2026-09-14 | M3 增加 `touchpoint_address_pages`，支持组织范围、内容类型、`target_url`、地址标识和启停；`touchpoint_payloads` 增加可空 `address_page_id`，实际内容不强制 HTTP/HTTPS 格式。 |

> 历史版本：V1.2 原文档保留为历史基线。
