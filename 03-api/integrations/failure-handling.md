# 外部系统故障处理

| 故障 | 首次处理 | 重试 | 任务/审计结果 | 人工处理 |
|---|---|---|---|---|
| LinkForty 来源 ACL 拒绝 | 记录网络拒绝和 `trace_id` | 不自动重试 | 外部调用失败；审计网络边界错误 | 是 |
| LinkForty 内网路由不可达 | 记录连通性失败和 `trace_id` | 按网络故障策略退避 | 任务待重试；审计失败 | 是 |
| LinkForty TLS 握手失败 | 拒绝调用并记录证书/连接错误摘要 | 不盲目重试 | 外部调用失败；告警 | 是 |
| LinkForty DNS 解析失败 | 记录解析失败和 `trace_id` | 按网络故障策略退避 | 任务待重试；审计失败 | 是 |
| LinkForty 超时 | 记录失败和 `trace_id` | 指数退避 | 任务待重试；审计失败 | 是 |
| LinkForty 4xx | 记录字段或权限错误 | 默认不重试 | 审计失败 | 是 |
| LinkForty 5xx | 记录平台错误 | 指数退避 | 任务待重试；审计失败 | 是 |
| Webhook 签名错误 | 拒绝 | 不自动重试 | 拒绝 | 安全排查 |
| Webhook 重复 | 查询唯一键 | 不重试 | 幂等成功 | 否 |
| 只读数据不可用 | 返回数据源错误 | 查询重试 | 数据源失败 | 是 |
| NFC 写入失败 | 记录设备操作失败 | 设备策略 | 任务失败；审计失败 | 是 |

表中的处理结果写入任务日志和 M1 的 `operation_logs`，不映射为 `touchpoint_payloads` 的同步状态字段。

## M5 访问事件关联重试（内部任务契约）

访问事件关联重试只通过 Celery 内部任务执行，不提供 `/retries`、
`/event-retries` 或人工重放 HTTP 路由，也不新增重试管理表。Router、Service、
Repository 和 Worker 的职责保持分离：Service 生成安全上下文，scheduler 负责
入队，Celery task 负责有限重试和最终失败审计。

`EventRetryContext.to_payload()` 生成的 `EventRetryPayload` 只有以下字段：

| 字段 | 类型和约束 |
| --- | --- |
| `event_id` | 非空字符串，最多 255 字符；全局幂等身份 |
| `access_event_id` | 可空正 BIGINT；以十进制字符串传输 |
| `click_id` | 可空标准 UUID 字符串 |
| `linkforty_link_id` | 可空标准 UUID 字符串 |
| `occurred_at` | 带时区 ISO 8601 时间字符串 |
| `received_at` | 带时区 ISO 8601 时间字符串 |
| `body_sha256` | 64 位十六进制 SHA-256 字符串；不保存 raw body |
| `trace_id` | 非空追踪字符串，最多 64 字符 |
| `retry_reason` | 非空内部原因字符串，最多 255 字符 |

BIGINT 不转换为 JavaScript Number；不得把 Webhook Secret、原始 body、敏感 Header
或未脱敏个人信息放入 payload、日志、审计或错误响应。任务 ID 由
`event_id` 的 SHA-256 派生，格式为 `m5-event-association-<sha256>`，同一事件
跨重试保持稳定。

`EventRetryPolicy` 默认最多重试 3 次，即最多 4 次执行；退避基准为 1 秒，按
指数增长并封顶 60 秒，默认无 jitter。配置项可以调整这些数值，但必须保持有限
重试、Celery 原生 task ID 和 `retry()` 返回语义。Malformed payload 使用
`REQUEST_SCHEMA_INVALID` 记录内部失败，不进入公共 HTTP 接口。
