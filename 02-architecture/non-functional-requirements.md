# 非功能需求

## 安全

- 所有后台 API 必须认证。
- 所有业务 API 必须执行功能权限和数据范围校验。
- 禁止保存密码、Token 或密码哈希。
- LinkForty 只读账号不得读取 `webhooks.secret`。
- 关键操作和导出必须审计。

## 可用性

- Webhook 接收失败可重试。
- LinkForty 发布失败可追踪和补偿。
- Redis 故障不能导致业务事实丢失。
- 数据库迁移和回滚必须可演练。

## 可观测性

统一记录 `request_id`、`trace_id`、`operator_id`、`event_id`、`click_id`、`external_request_id` 和 `celery_task_id`。

## 性能

- 列表查询必须分页。
- 排序字段必须白名单控制。
- 统计查询必须使用明确时间范围。
- 高频过滤字段建立索引。
- 导出大数据量时采用异步任务。
