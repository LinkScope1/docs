# 权限与 API 映射

| 权限编码 | 方法 | 路径 | 数据范围 | 是否审计 |
|---|---|---|---|---|
| org.read | GET | `/api/v1/organizations` | 本人/机构/全局 | 否 |
| org.manage | POST/PATCH | `/api/v1/organizations/**` | 机构/全局 | 是 |
| manager.read | GET | `/api/v1/customer-managers` | 本人/机构/全局 | 否 |
| manager.manage | POST/PATCH | `/api/v1/customer-managers/**` | 机构/全局 | 是 |
| touchpoint.asset.read | GET | `/api/v1/touchpoint-assets` | 本人/机构/全局 | 否 |
| touchpoint.asset.manage | POST/PATCH | `/api/v1/touchpoint-assets/**` | 机构/全局 | 是 |
| touchpoint.assignment.manage | POST | `/api/v1/touchpoint-assignments/**` | 机构/全局 | 是 |
| target-resource.manage | POST/PATCH | `/api/v1/target-resources/**` | 机构/全局 | 是 |
| routing-rule.publish | POST | `/api/v1/routing-rules/*/publish` | 机构/全局 | 是 |
| access-event.read | GET | `/api/v1/access-events` | 本人/机构/全局 | 否 |
| analytics.export | GET | `/api/v1/analytics/export` | 本人/机构/全局 | 是 |
| audit.read | GET | `/api/v1/audit-logs` | 机构/全局 | 否 |
