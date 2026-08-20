# 监控方案

## 指标

- API 请求成功率和响应时间。
- 数据库连接池使用率。
- Redis 连接状态。
- Celery 队列长度和失败数。
- LinkForty API 失败率和延迟。
- LinkForty API 重试和补偿失败数。
- LinkForty 网络连通性失败数。
- LinkForty DNS 解析失败数。
- LinkForty TLS 握手失败数。
- LinkForty 请求超时数。
- LinkForty HTTP 失败数。
- Webhook 验签失败数。
- Webhook 解析失败数。
- 批量导入失败数。
- 统计查询耗时。
- 导出任务失败数。
- M1 操作审计写入失败数。

## 统一关联字段

`request_id`、`trace_id`、`operator_id`、`event_id`、`click_id`、`external_request_id`、`celery_task_id`。
