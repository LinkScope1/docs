# V1.3.2 权限与 API 映射

Casdoor 是权限编码唯一来源。以下编码是 V1.3.2 本地冻结契约；Casdoor 正式导出是外部配置验收证据。前端 `data-testid` 不得复用权限编码。

| 权限编码 | 方法 | 路径 | 数据范围 | 审计 |
|---|---|---|---|---:|
| `authenticated` | GET | `/api/v1/auth/me` | `EMPLOYEE_SELF` | 否 |
| `organization.read` | GET | `/api/v1/organizations`、`/api/v1/organizations/tree`、`/api/v1/organizations/{id}` | `ORG_SUBTREE` | 否 |
| `organization.manage` | POST/PATCH/POST command | `/api/v1/organizations/**` | `ORG_SUBTREE` | 是 |
| `employee.read` | GET | `/api/v1/employees`、`/api/v1/employees/{id}`、`/api/v1/employees/{id}/associated-cards` | `ORG_SUBTREE` | 否 |
| `employee.manage` | POST/PATCH/POST command | `/api/v1/employees/**` | `ORG_SUBTREE` | 是 |
| `employee.delete` | DELETE | `/api/v1/employees/{id}` | `ORG_SUBTREE` | 是；仅允许已停用且无当前责任员工 |
| `employee.transfer` | POST | `/api/v1/employees/{id}/transfer` | `SOURCE_AND_TARGET_ORG` | 是 |
| `touchpoint.asset.read` | GET | `/api/v1/touchpoint-assets`、`/api/v1/touchpoint-assets/{id}` | `ASSET_SCOPE` | 否 |
| `touchpoint.asset.manage` | POST/PATCH/POST command | `/api/v1/touchpoint-assets/**` | `ORG_SUBTREE`/`ASSET_SCOPE` | 是 |
| `touchpoint.asset.scrap` | POST | `/api/v1/touchpoint-assets/{id}/scrap` | `ASSET_SCOPE` | 是 |
| `touchpoint.payload.read` | GET | `/api/v1/touchpoint-payloads`、`/api/v1/touchpoint-payloads/{id}`、`/api/v1/touchpoint-assets/{assetId}/payloads` | `ASSET_SCOPE` | 否 |
| `touchpoint.payload.manage` | POST/PATCH/POST command | `/api/v1/touchpoint-payloads/**`、`/api/v1/touchpoint-assets/{assetId}/payloads` | `ASSET_SCOPE` | 是 |
| `touchpoint.address-page.read` | GET | `/api/v1/touchpoint-address-pages`、`/api/v1/touchpoint-address-pages/{id}`、`/api/v1/touchpoint-address-pages/options`、`/api/v1/touchpoint-address-pages/**` | `ORG_SUBTREE`；选项叠加 `ASSET_SCOPE` | 否 |
| `touchpoint.address-page.manage` | POST/PATCH/POST command | `/api/v1/touchpoint-address-pages/**` | `ORG_SUBTREE` | 是 |
| `touchpoint.address-page.delete` | DELETE | `/api/v1/touchpoint-address-pages/{id}` | `ORG_SUBTREE` | 是；仅允许已停用且无排队/执行中重新应用任务 |
| `touchpoint.assignment.read` | GET | `/api/v1/touchpoint-assignments`、`/api/v1/touchpoint-assignments/{id}` | `ASSET_SCOPE` | 否 |
| `touchpoint.assignment.manage` | POST | `/api/v1/touchpoint-assignments`、`/api/v1/touchpoint-assignments/{id}/unbind` | `ASSET_SCOPE` | 是 |
| `touchpoint.assignment.transfer` | POST | `/api/v1/touchpoint-assignments/transfer` | `SOURCE_AND_TARGET_ORG` | 是 |
| `access-event.read` | GET | `/api/v1/access-events`、`/api/v1/access-events/{id}` | `ORG_SUBTREE`/`EMPLOYEE_SELF` | 否 |
| `analytics.read` | GET | `/api/v1/analytics/summary` | `ORG_SUBTREE` | 否 |
| `import.validate` | POST | `/api/v1/imports/validate` | `ORG_SUBTREE`，按模板资源再收窄 | 是 |
| `import.validate` | GET | `/api/v1/imports/templates/{templateType}`、`/api/v1/imports/templates/employees` | `ORG_SUBTREE` | 否 |
| `import.validate` | POST | `/api/v1/imports/execute` | `ORG_SUBTREE`，执行时叠加业务管理权限 | 是 |
| `import.validate` | GET | `/api/v1/imports/{batchId}`、`/api/v1/imports/{batchId}/failure-report` | `EMPLOYEE_SELF`；全局管理员可查看 | 否 |
| `employee.manage` | POST | `/api/v1/imports/employees/execute` | `ORG_SUBTREE` | 是 |
| `import.validate` | GET | `/api/v1/imports/templates/organizations` | `ORG_SUBTREE` | 否 |
| `organization.manage` | POST | `/api/v1/imports/organizations/execute` | `ORG_SUBTREE` | 是 |
| `export.read` | GET | `/api/v1/exports/{resource}` | `ORG_SUBTREE`，按资源再收窄为 `ASSET_SCOPE` | 是 |
| `export.payload-content` | GET | `/api/v1/exports/touchpoint-payloads?mode=content` | 在 `export.read` 数据范围内 | 是 |
| `audit.read` | GET | `/api/v1/audit-logs`、`/api/v1/audit-logs/{id}` | `ORG_SUBTREE` | 否 |

关联卡详情接口虽然以 `employee.read` 作为路由入口权限，但后端 Service 还必须同时校验
`touchpoint.assignment.read` 和 `touchpoint.asset.read` 及 `ASSET_SCOPE`；缺少任一权限返回
`403`。员工列表在缺少这两项关联卡读取权限时将 `associatedCardCount` 返回为 `null`，不表示数量为零。

`system_webhook` 仅表示 LinkForty Webhook 的 HMAC 集成主体，不是 Casdoor 用户权限，也不进入角色矩阵。

认证入口 `/api/v1/auth/login`、`/api/v1/auth/callback` 和 `/api/v1/auth/logout` 使用 `public` 契约标识，不属于 M1～M5 功能权限矩阵；`/api/v1/auth/me` 和所有业务接口使用服务端 `bank_admin_session` Cookie。业务请求不再通过浏览器携带 Bearer Token。

## Scope 定义

- `GLOBAL`：全量银行数据。
- `ORG_SUBTREE`：当前授权组织及其编码前缀表示的下级组织。
- `ORG_SELF`：当前员工直接所属组织，不含下级组织。
- `EMPLOYEE_SELF`：当前员工直接责任数据。
- `ASSET_SCOPE`：资源 `org_id` 在授权范围内；员工角色额外限制为本人责任资产或本机构库存资产。
- `SOURCE_AND_TARGET_ORG`：来源和目标组织均在授权范围内，且调用方具备 Transfer 权限。

三类业务导入统一使用 `/api/v1/imports/validate` 和 `/api/v1/imports/execute`；超过 1,000 行由 Celery 异步执行，使用 `batchId` 查询结果。普通载体内容导出不含原始内容值，原值导出必须额外具备 `export.payload-content` 权限并二次确认。统计不拥有本地表，导出不创建对象存储或下载 Token。
