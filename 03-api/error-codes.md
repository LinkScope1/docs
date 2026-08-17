# 错误码清单

| 错误码 | HTTP | 说明 |
|---|---:|---|
| AUTH_INVALID_TOKEN | 401 | Token 无效或过期 |
| AUTH_USER_DISABLED | 403 | 用户已停用 |
| PERMISSION_DENIED | 403 | 无功能权限 |
| DATA_SCOPE_DENIED | 403 | 超出数据范围 |
| RESOURCE_NOT_FOUND | 404 | 对象不存在 |
| VALIDATION_ERROR | 400 | 参数校验失败 |
| DUPLICATE_CODE | 409 | 编码重复 |
| STATE_CONFLICT | 409 | 状态不允许当前操作 |
| ASSIGNMENT_CONFLICT | 409 | 绑定时间或唯一性冲突 |
| ROUTING_RULE_CONFLICT | 409 | 路由规则冲突 |
| IDEMPOTENCY_REPLAY | 200 | 重复命令已处理 |
| WEBHOOK_SIGNATURE_INVALID | 401 | Webhook 签名错误 |
| WEBHOOK_EVENT_ID_MISSING | 400 | 缺少 event_id |
| EXTERNAL_API_TIMEOUT | 504 | 外部 API 超时 |
| EXTERNAL_API_ERROR | 502 | 外部 API 失败 |
| DATA_SOURCE_UNAVAILABLE | 503 | 数据源不可用 |
| EXPORT_NOT_ALLOWED | 403 | 无导出权限 |
| INTERNAL_ERROR | 500 | 未预期错误 |
