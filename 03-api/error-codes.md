# 错误码清单

本文档是 M1–M5 业务错误码及其 HTTP 状态码映射的唯一权威来源。API 响应结构和 HTTP 通用语义参见 [API 规范](./api-guidelines.md)。

| 错误码 | HTTP | 说明 |
| --- | ---: | --- |
| `AUTH_INVALID_TOKEN` | 401 | Token 无效或过期 |
| `AUTH_USER_DISABLED` | 403 | 用户已停用 |
| `AUTH_ORIGIN_NOT_ALLOWED` | 403 | 携带 Session Cookie 的写请求来源不在允许的 Origin 列表 |
| `PERMISSION_DENIED` | 403 | 无功能权限 |
| `DATA_SCOPE_DENIED` | 403 | 超出组织或员工数据范围 |
| `RESOURCE_NOT_FOUND` | 404 | 业务对象不存在 |
| `VALIDATION_ERROR` | 400 | 业务参数组合或规则校验失败 |
| `REQUEST_SCHEMA_INVALID` | 422 | 字段缺失、类型或格式校验失败 |
| `DUPLICATE_CODE` | 409 | 业务编码重复 |
| `STATE_CONFLICT` | 409 | 当前状态不允许执行该操作 |
| `ASSIGNMENT_CONFLICT` | 409 | 绑定时间重叠或当前绑定冲突 |
| `WEBHOOK_SIGNATURE_INVALID` | 401 | Webhook 签名错误 |
| `WEBHOOK_EVENT_ID_MISSING` | 400 | Webhook 缺少 `event_id` |
| `EXTERNAL_API_TIMEOUT` | 504 | 外部 API 调用超时 |
| `EXTERNAL_API_ERROR` | 502 | 外部 API 返回失败 |
| `DATA_SOURCE_UNAVAILABLE` | 503 | 数据源暂时不可用 |
| `EXPORT_NOT_ALLOWED` | 403 | 当前人员无导出权限 |
| `EXPORT_LIMIT_EXCEEDED` | 413 | 同步导出超过 10 MiB 或 100,000 行限制 |
| `NOT_IMPLEMENTED` | 501 | 已定义但尚未实现的工程占位能力 |
| `INTERNAL_ERROR` | 500 | 未预期的系统错误 |

## 使用规则

- 错误码使用稳定的英文大写蛇形命名。
- HTTP 状态码表达协议结果，错误码表达具体业务原因。
- 相同错误码不得在不同模块中表达不同含义。
- 中文 `message` 可以按资源类型具体描述，但不得改变错误码含义。例如组织、员工或载体不存在均使用 `RESOURCE_NOT_FOUND`。
- `VALIDATION_ERROR` 用于字段类型正确但业务组合或规则不成立；FastAPI 请求字段缺失、类型或格式错误统一使用 `REQUEST_SCHEMA_INVALID`。
- 幂等重放成功不是错误，不进入本清单；处理规则参见 [幂等规范](./idempotency.md)。
- 模块新增错误码时必须同步更新 OpenAPI、实现和自动测试。

## M5 内部/非 HTTP 错误码

以下代码只用于访问事件投影、Celery 重试、审计和告警的内部状态或
`resolutionReason`，不作为公共 HTTP `error.code`，也不新增对应的公共 API：

| 错误码 | 内部用途 |
| --- | --- |
| `IDEMPOTENT_REPLAY` | 已存在的 `event_id` 被重复投递并按幂等成功处理 |
| `BINDING_NOT_FOUND` | 按事件发生时间未找到可用历史绑定 |
| `STATE_UPDATE_FAILED` | 访问事件状态更新失败 |
| `EVENT_RETRY_ENQUEUE_FAILED` | 重试任务在数据库事务完成后入队失败 |
| `AUDIT_WRITE_FAILED` | 操作审计或失败审计写入失败 |
| `FINAL_FAILURE_ALREADY_RECORDED` | 终态失败已记录，避免重复写入失败事实 |

这些内部代码仍须通过 `operation_logs`、任务结果或告警保留可追踪性；对外
错误响应继续使用本文件上方定义的公共代码，例如 `REQUEST_SCHEMA_INVALID`、
`STATE_CONFLICT`、`DATA_SOURCE_UNAVAILABLE` 或 `INTERNAL_ERROR`。
