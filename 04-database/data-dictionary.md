# V1.3.2 数据字典

## 物理表范围

V1.3.2 业务库保留 7 张表。Casdoor 是身份、角色和功能权限来源，银行库不再创建任何 `iam_*` 表；目标资源和路由规则暂不属于本版本。

| 序号 | 表 | 归属模块 | 用途 |
|---:|---|---|---|
| 1 | `organization_units` | M2 | 使用组织编码前缀表示层级的组织表 |
| 2 | `employees` | M2 | 员工主数据和组织归属 |
| 3 | `touchpoint_assets` | M3 | NFC 触点载体 |
| 4 | `touchpoint_payloads` | M3 | 载体实际写入内容 |
| 5 | `touchpoint_employee_assignments` | M4 | 载体与员工的当前及历史绑定 |
| 6 | `access_events` | M5 | Webhook 访问事件投影和关联结果 |
| 7 | `operation_logs` | M1 | 员工和系统操作审计 |

### 通用约定

- 主键使用 BIGINT 雪花 ID，API 以字符串传输。
- LinkForty 外部对象继续使用 UUID；跨系统关系为逻辑引用。
- 时间统一使用 `TIMESTAMPTZ`。
- `org_id` 表示数据责任组织，`employee_id` 表示直接责任员工；系统事件或公共数据的 `employee_id` 可以为空。
- 员工表以 `id` 作为员工 ID，不增加自指 `employee_id`。
- 业务表不依赖数据库级级联删除；关系完整性由 Service/Repository 事务校验。

## 1. organization_units

组织表不使用 `parent_org_id`。`org_code` 按根节点 `1`、每级追加三位数字的前缀分段规则表达层级，例如 `1` → `1001` → `1001001`。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
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

直接子级由应用校验为父编码追加恰好三位数字；下级查询使用编码前缀，不保存 `org_type`、`parent_org_id`、`source_type` 或 `external_org_id`。

## 2. employees

员工主数据使用 `employees` 表。Casdoor Token 的 `employee_code` Claim 用于定位员工；员工表不保存身份平台映射字段或外部员工来源字段。

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
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

## 3. touchpoint_assets

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_code | VARCHAR(64) | 否 | — | 系统业务编码，唯一 |
| asset_type | SMALLINT | 否 | 1 | 1 NFC；一期固定使用 NFC |
| carrier_uid | VARCHAR(128) | 是 | — | NFC 物理 UID；非空时唯一 |
| org_id | BIGINT | 否 | — | 当前数据责任组织 |
| employee_id | BIGINT | 是 | — | 当前直接责任员工；库存时可空 |
| asset_status | SMALLINT | 否 | 0 | 0 库存 / 1 启用 / 2 停用 / 9 永久作废 |
| supplier_code | VARCHAR(64) | 是 | — | 供应商编码 |
| supplier_batch_no | VARCHAR(64) | 是 | — | 供应商批次 |
| metadata | JSONB | 否 | `{}` | 载体扩展属性对象 |
| description | VARCHAR(500) | 是 | — | 说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

资产字段仅承载 `asset_code`、`carrier_uid`、责任范围和供应商信息；位置属性由组织表维护。`asset_code` 用于系统业务和导入，`carrier_uid` 用于物理盘点，两者不互相替代。

## 4. touchpoint_payloads

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_id | BIGINT | 否 | — | 所属载体逻辑引用 |
| org_id | BIGINT | 否 | — | 从载体同步的数据责任组织 |
| employee_id | BIGINT | 是 | — | 从载体同步的直接责任员工 |
| payload_type | SMALLINT | 否 | 1 | 1 短链 / 2 URL / 3 文本 / 99 其他 |
| payload_value | VARCHAR(2048) | 否 | — | 卡内实际写入内容，不是最终目标 |
| payload_source | SMALLINT | 否 | — | 1 供应商预写 / 2 本系统 / 3 外部导入 / 4 人工录入 |
| provider_type | SMALLINT | 否 | 1 | 1 LinkForty / 2 供应商 / 3 无平台 / 99 其他 |
| linkforty_link_id | UUID | 是 | — | LinkForty 链接逻辑引用 |
| status | SMALLINT | 否 | 0 | 0 待登记 / 1 有效 / 2 停用 / 3 失效 |
| metadata | JSONB | 否 | `{}` | 低频扩展属性对象 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 修改时间 |

`linkforty_link_id` 仅为 LinkForty 逻辑引用。`touchpoint_payloads` 不保存专属同步状态、核验状态、同步时间、错误摘要、重试次数或其他替代字段。

## 5. touchpoint_employee_assignments

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
| id | BIGINT | 否 | 雪花算法 | PK |
| asset_id | BIGINT | 否 | — | 载体逻辑引用 |
| org_id | BIGINT | 否 | — | 绑定记录责任组织 |
| employee_id | BIGINT | 否 | — | 绑定员工 |
| assignment_status | SMALLINT | 否 | 1 | 1 当前有效 / 2 已解绑 |
| effective_from | TIMESTAMPTZ | 否 | NOW() | 生效时间 |
| effective_to | TIMESTAMPTZ | 是 | — | 失效时间 |
| unbind_reason_type | SMALLINT | 是 | — | 解绑原因码 |
| unbind_reason | VARCHAR(500) | 是 | — | 解绑说明 |
| created_by_employee_id | BIGINT | 是 | — | 创建员工逻辑引用 |
| updated_by_employee_id | BIGINT | 是 | — | 最后修改员工逻辑引用；绑定、解绑或其他允许修改绑定记录的操作均更新 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 记录时间 |
| updated_at | TIMESTAMPTZ | 否 | NOW() | 最后更新时间 |

不保存组织名称、支行名称或员工名称快照。创建和最后修改员工使用逻辑引用，完整操作员工、操作时间、前后数据和结果通过 `operation_logs` 记录。记录只追加，当前资产最多一条有效绑定，所有有效时间区间不得重叠。

## 6. access_events

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
| id | BIGINT | 否 | 雪花算法 | PK |
| event_id | VARCHAR(255) | 否 | — | Webhook 全局唯一幂等键 |
| click_id | UUID | 否 | — | LinkForty 点击逻辑引用，非唯一 |
| asset_id | BIGINT | 否 | — | 访问载体 |
| binding_id | BIGINT | 是 | — | 事件时命中的绑定记录 |
| org_id | BIGINT | 是 | — | 事件关联组织 |
| employee_id | BIGINT | 是 | — | 事件关联员工 |
| resolution_status | SMALLINT | 否 | 0 | 0 待关联 / 1 成功 / 2 待重试 / 3 失败 |
| resolution_reason | VARCHAR(255) | 是 | — | 关联结果摘要 |
| event_metadata | JSONB | 否 | `{}` | 低频事件属性对象 |
| resolved_at | TIMESTAMPTZ | 是 | — | 当前关联尝试完成时间 |
| received_at | TIMESTAMPTZ | 否 | NOW() | 首次接收时间，不更新 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 本地写入时间 |

事件表仅保存资产、绑定、组织和员工关联字段，不保存路由目标或名称快照；事件关联状态不表示目标解析。

## 7. operation_logs

| 字段 | 类型 | 可空 | 默认值 | 约束/说明 |
|---|---|---:|---|---|
| id | BIGINT | 否 | 雪花算法 | PK |
| trace_id | VARCHAR(64) | 否 | — | 请求或批次追踪号 |
| org_id | BIGINT | 是 | — | 本次操作数据范围 |
| employee_id | BIGINT | 是 | — | 操作员工；系统任务可空 |
| operation_type | SMALLINT | 否 | — | 1 登录 / 2 创建 / 3 修改 / 4 启停 / 5 绑定 / 6 解绑 / 7 调拨 / 8 导入 / 9 导出 / 10 外部同步 / 99 其他 |
| object_type | SMALLINT | 否 | — | 1 组织 / 2 员工 / 3 载体 / 4 内容 / 5 绑定 / 6 事件 / 7 导入 / 99 其他 |
| object_id | BIGINT | 是 | — | 本系统对象 ID |
| external_object_id | UUID | 是 | — | 外部对象 ID |
| operation_result | SMALLINT | 否 | — | 1 成功 / 2 失败 / 3 部分成功 |
| operation_summary | VARCHAR(1000) | 是 | — | 摘要 |
| operation_detail | JSONB | 否 | `{}` | 请求 ID、批次号、影响数量等 |
| before_data | JSONB | 是 | — | 修改前必要字段 |
| after_data | JSONB | 是 | — | 修改后必要字段 |
| error_code | VARCHAR(64) | 是 | — | 错误码 |
| error_message | VARCHAR(500) | 是 | — | 错误摘要 |
| ip_cipher | VARCHAR(256) | 是 | — | 加密 IP |
| ip_hash | VARCHAR(64) | 是 | — | IP 哈希 |
| user_agent | VARCHAR(512) | 是 | — | 客户端 |
| operation_time | TIMESTAMPTZ | 否 | NOW() | 操作时间 |
| created_at | TIMESTAMPTZ | 否 | NOW() | 写入时间 |

日志只追加，不记录密码、Token、密钥、Webhook Secret 或未脱敏隐私信息。
