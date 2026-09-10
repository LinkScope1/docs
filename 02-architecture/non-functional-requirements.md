# 非功能需求

## 安全

- 面向浏览器、用户和业务调用方的银行后台 API 必须认证。
- 银行后台至 LinkForty Core 的出站服务间调用采用登记的网络隔离安全例外：使用私有网络、来源 ACL、防火墙、私有 DNS、HTTPS/TLS 和网络审计，不使用应用层 API Key、JWT、OAuth 或其他调用凭证。
- 所有业务 API 必须执行功能权限和数据范围校验。
- 禁止保存密码、Token 或密码哈希。
- LinkForty 只读账号不得读取 `webhooks` 或 `webhooks.secret`；Webhook Secret 只能通过受控 Core API provisioning 一次性交付给银行配置服务。
- Secret 仅作为银行后台验签的受保护运行时配置，不写入银行业务表、日志、审计、fixture、文档或前端状态。
- 关键操作和导出必须审计。

LinkForty 的网络隔离例外不改变银行后台用户 API 的 BFF Session Cookie 认证、服务端 Casdoor OIDC/JWT 验证要求，也不替代 LinkForty Webhook 的 HMAC 签名验证。Core 管理 API 当前不使用应用层认证，provisioning 只能从银行后台服务网段通过私有网络、来源 ACL、防火墙、私有 DNS、HTTPS/TLS 和网络审计执行。生产启用该例外前必须取得安全负责人审批；网络区域内其他被攻陷服务可能冒用银行后台调用 LinkForty Core。

## 可用性

- Webhook 接收失败可重试。
- LinkForty API 调用失败可追踪、重试和补偿。
- Redis 故障不能导致业务事实丢失。
- 数据库迁移和回滚必须可演练。

## 可观测性

统一记录 `request_id`、`trace_id`、`operator_id`、`event_id`、`click_id`、`external_request_id` 和 `celery_task_id`。外部调用结果必须能够关联 M1 的 `operation_logs`，但不得依赖 Payload 同步状态字段。

## 性能

- 列表查询必须分页。
- 排序字段必须白名单控制。
- 统计查询必须使用明确时间范围。
- 高频过滤字段建立索引。
- 导出大数据量时采用异步任务。
