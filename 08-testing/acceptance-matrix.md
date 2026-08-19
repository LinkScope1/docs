# V1.3.2 验收矩阵

| 需求编号 | 模块 | API/对象 | 测试用例 | 状态 |
|---|---|---|---|---|
| M1-001 | Casdoor 登录 | `/auth/me` | JWT、Claim 缺失、停用员工、越权 | 待测 |
| M2-001 | 组织维护 | `organization_units` | 编码唯一、前缀分段、停用阻断 | 待测 |
| M2-002 | 员工维护 | `employees` | 员工编码唯一、组织范围、状态 | 待测 |
| M3-001 | 触点资产 | `touchpoint_assets` | 资产编码、UID 唯一、状态、范围字段 | 待测 |
| M3-002 | 载体内容 | `touchpoint_payloads` | 内容类型、实际写入值、范围同步、LinkForty 逻辑引用、无本地同步状态字段 | 待测 |
| M4-001 | 绑定 | `touchpoint_employee_assignments` | 重叠、当前唯一、历史无快照、转交 | 待测 |
| M5-001 | Webhook | `access_events` | 签名、幂等、重复 click、关联重试 | 待测 |
| CAP-ANL-001 | 统计与报表横向能力（不编号） | analytics | 时间、机器人、范围、只读边界、审计 | 待测 |
| IMP-001 | 文档导入预留 | `/imports/validate` | 模板、稳定匹配键、逐行错误 | 待测 |
| IMP-002 | 文档导入预留 | `/imports/execute` | 更新并新增、幂等、显式解绑、审计 | 待测 |
