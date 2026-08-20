# 运维手册

## Webhook 大量失败

1. 查询失败率和错误码。
2. 检查签名配置是否变更。
3. 检查 API 和数据库连通性。
4. 检查任务队列积压。
5. 暂停自动重试或调整退避。
6. 修复原因后执行小批量重试。
7. 核对 `access_events` 数量。

## LinkForty 外部调用失败

1. 从告警或请求上下文取得 `trace_id`、`external_request_id` 和 `celery_task_id`。
2. 按 `trace_id` 查询 M1 的 `operation_logs`、Worker 任务日志和外部请求日志。
3. 检查 DNS 解析、内网路由、防火墙、来源 ACL 和 LinkForty Core 服务端 TLS 证书。
4. 判断是否为网络拒绝、TLS 握手失败、参数、超时或平台错误。
5. 参数错误和 TLS 证书错误不得盲目重试。
6. 网络暂时不可达或平台错误按策略重试或执行补偿。
7. 最终失败转人工处理，并核对 `operation_logs` 的结果和错误摘要。

不得通过查询或修改 `touchpoint_payloads` 同步状态字段处理故障。

LinkForty 出站调用不使用 API Key、JWT、OAuth 或 mTLS 客户端证书；不得为排查故障临时把应用层凭证写入配置、日志或命令行参数。

## 数据库连接异常

- 检查数据库健康状态。
- 检查连接池和慢查询。
- 检查最近迁移。
- 禁止绕过应用直接修改业务数据。
