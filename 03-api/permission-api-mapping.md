# V1.3.2 权限与 API 映射

| 权限编码 | 方法 | 路径 | 数据范围 | 是否审计 |
|---|---|---|---|---|
| org.read | GET | `/api/v1/organizations` | 组织编码前缀 | 否 |
| org.manage | POST/PATCH | `/api/v1/organizations/**` | 机构/全局 | 是 |
| employee.read | GET | `/api/v1/employees` | `org_id` | 否 |
| employee.manage | POST/PATCH | `/api/v1/employees/**` | `org_id` | 是 |
| touchpoint.asset.read | GET | `/api/v1/touchpoint-assets` | `org_id`/`employee_id` | 否 |
| touchpoint.asset.manage | POST/PATCH | `/api/v1/touchpoint-assets/**` | `org_id`/`employee_id` | 是 |
| touchpoint.payload.manage | POST/PATCH | `/api/v1/touchpoint-payloads/**` | `org_id`/`employee_id` | 是 |
| touchpoint.assignment.manage | POST | `/api/v1/touchpoint-assignments/**` | `org_id`/`employee_id` | 是 |
| import.execute | POST | `/api/v1/imports/execute` | 与页面查询一致 | 是 |
| access-event.read | GET | `/api/v1/access-events` | 事件 `org_id`/`employee_id` | 否 |
| analytics.export | GET | `/api/v1/analytics/export` | 与页面查询一致 | 是 |
| audit.read | GET | `/api/v1/audit-logs` | 日志 `org_id` | 否 |

`analytics.export` 属于非编号统计与报表横向能力，不新增业务模块编号或本地数据所有权。目标资源、路由规则及发布权限不属于 V1.3.2。
