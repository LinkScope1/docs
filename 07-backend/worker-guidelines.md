# 异步任务规范

## 适用场景

- LinkForty API 调用重试和补偿。
- Webhook 解析重试。
- 外部调用结果对账。
- 大数据量导出。

## 要求

- 任务必须有稳定任务 ID。
- 任务必须幂等。
- 任务必须记录开始、成功、失败和最终处理结果，并将结果关联到 `trace_id` 和 M1 的 `operation_logs`。
- 重试次数和退避策略可配置。
- 达到最终失败后进入人工处理队列；不得在 `touchpoint_payloads` 中新增同步状态字段。
- Redis 不能作为唯一业务事实来源。

## 地址页面重新应用任务

- 地址页面目标配置变更只在地址页面本地事务中写入主数据和审计；事务提交后再创建
  `touchpoint_address_page_reapply_jobs` 及明细，随后投递 Celery 任务。
- 任务保存 `page_config_hash`、请求人和请求组织的安全快照、总数与成功/失败计数；明细保存
  Payload、尝试次数、Link ID 和脱敏错误摘要。
- Worker 根据任务明细重新查询并校验页面、资产、Payload、提供方和组织层级，逐条调用
  `apply_address_page_to_payload`；不信任客户端资产列表，也不在持有本地锁时调用外部 HTTP。
- 页面版本变化时旧任务明细必须失败并返回 `PAGE_VERSION_CONFLICT`，不能覆盖新页面配置。
- `GET /touchpoint-address-pages/{id}/reapply-tasks/{taskId}` 和 retry 接口每次重新执行页面
  组织范围校验；重试只把失败明细重新置为 queued。
