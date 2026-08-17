# 监控方案

## 指标

- API 请求成功率和响应时间。
- 数据库连接池使用率。
- Redis 连接状态。
- Celery 队列长度和失败数。
- LinkForty API 失败率和延迟。
- Webhook 验签失败数。
- Webhook 解析失败数。
- 路由发布失败数。
- 批量导入失败数。
- 统计查询耗时。
- 导出任务失败数。
- IAM 投影同步失败数。

## 统一关联字段

`request_id`、`trace_id`、`operator_id`、`event_id`、`click_id`、`external_request_id`、`celery_task_id`。
