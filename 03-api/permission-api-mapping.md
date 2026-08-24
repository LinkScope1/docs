# V1.3.2 权限与 API 映射

Casdoor 是权限编码唯一来源。以下编码是 V1.3.2 本地冻结契约；Casdoor 正式导出是外部配置验收证据。前端 `data-testid` 不得复用权限编码。

| 权限编码 | 方法 | 路径 | 数据范围 | 审计 |
|---|---|---|---|---:|
| `authenticated` | GET | `/api/v1/auth/me` | `EMPLOYEE_SELF` | 否 |
| `organization.read` | GET | `/api/v1/organizations`、`/api/v1/organizations/{id}` | `ORG_SUBTREE` | 否 |
| `organization.manage` | POST/PATCH/POST command | `/api/v1/organizations/**` | `ORG_SUBTREE` | 是 |
| `employee.read` | GET | `/api/v1/employees`、`/api/v1/employees/{id}` | `ORG_SUBTREE` | 否 |
| `employee.manage` | POST/PATCH/POST command | `/api/v1/employees/**` | `ORG_SUBTREE` | 是 |
| `employee.transfer` | POST | `/api/v1/employees/{id}/transfer` | `SOURCE_AND_TARGET_ORG` | 是 |
| `touchpoint.asset.read` | GET | `/api/v1/touchpoint-assets`、`/api/v1/touchpoint-assets/{id}` | `ASSET_SCOPE` | 否 |
| `touchpoint.asset.manage` | POST/PATCH/POST command | `/api/v1/touchpoint-assets/**` | `ORG_SUBTREE`/`ASSET_SCOPE` | 是 |
| `touchpoint.asset.scrap` | POST | `/api/v1/touchpoint-assets/{id}/scrap` | `ASSET_SCOPE` | 是 |
| `touchpoint.payload.read` | GET | `/api/v1/touchpoint-payloads`、`/api/v1/touchpoint-payloads/{id}` | `ASSET_SCOPE` | 否 |
| `touchpoint.payload.manage` | POST/PATCH/POST command | `/api/v1/touchpoint-payloads/**` | `ASSET_SCOPE` | 是 |
| `touchpoint.assignment.read` | GET | `/api/v1/touchpoint-assignments`、`/api/v1/touchpoint-assignments/{id}` | `ASSET_SCOPE` | 否 |
| `touchpoint.assignment.manage` | POST | `/api/v1/touchpoint-assignments`、`/api/v1/touchpoint-assignments/{id}/unbind` | `ASSET_SCOPE` | 是 |
| `touchpoint.assignment.transfer` | POST | `/api/v1/touchpoint-assignments/transfer` | `SOURCE_AND_TARGET_ORG` | 是 |
| `access-event.read` | GET | `/api/v1/access-events`、`/api/v1/access-events/{id}` | `ORG_SUBTREE`/`EMPLOYEE_SELF` | 否 |
| `analytics.read` | GET | `/api/v1/analytics/summary` | `ORG_SUBTREE` | 否 |
| `import.validate` | POST | `/api/v1/imports/validate` | `ORG_SUBTREE`，按模板资源再收窄 | 是 |
| `export.read` | GET | `/api/v1/exports/{resource}` | `ORG_SUBTREE`，按资源再收窄为 `ASSET_SCOPE` | 是 |
| `audit.read` | GET | `/api/v1/audit-logs`、`/api/v1/audit-logs/{id}` | `ORG_SUBTREE` | 否 |

`system_webhook` 仅表示 LinkForty Webhook 的 HMAC 集成主体，不是 Casdoor 用户权限，也不进入角色矩阵。

## Scope 定义

- `GLOBAL`：全量银行数据。
- `ORG_SUBTREE`：当前授权组织及其编码前缀表示的下级组织。
- `ORG_SELF`：当前员工直接所属组织，不含下级组织。
- `EMPLOYEE_SELF`：当前员工直接责任数据。
- `ASSET_SCOPE`：资源 `org_id` 在授权范围内；员工角色额外限制为本人责任资产或本机构库存资产。
- `SOURCE_AND_TARGET_ORG`：来源和目标组织均在授权范围内，且调用方具备 Transfer 权限。

V1.3.2 不提供 `/api/v1/imports/execute`；异步导入执行延期 V1.4。统计不拥有本地表，导出不创建对象存储或下载 Token。
