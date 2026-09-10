# LinkForty API 集成契约

## 状态

网络访问方式已确定；本地 Core 代码可观察到 `POST /api/links` 和
`GET /api/links/:id`，但正式字段、错误和网络安全边界仍必须由平台负责人以接口样例确认。Core 当前不执行 `Idempotency-Key` 服务端去重；同 Key 重复创建是 V1.3.2 已知限制。

## 调用安全边界

银行后台直接通过私有网络调用 LinkForty Core，不经过 API 网关或其他中间代理。

```text
认证方式：网络层访问控制
应用层认证：不使用
API Key：不使用
JWT/OAuth：不使用
mTLS 客户端证书：不使用
issuer/audience/subject：不适用
API Credential：不适用
```

网络控制要求：

- 仅允许指定银行后台服务网段访问；
- 使用来源 ACL、防火墙、私有 DNS 和 HTTPS/TLS；
- 校验 LinkForty Core 服务端证书；
- LinkForty Core 管理 API 不暴露公网；
- 记录 `trace_id`、`external_request_id`、耗时、连通性失败和调用结果；
- 生产启用该例外前必须取得安全负责人审批。

## 需要覆盖

- 创建 Link。
- 查询 Link。
- 查询点击分析事实。
- 网络访问方式和安全例外。
- 请求超时。
- 错误码。
- 限流。
- 幂等。
- 缓存失效。

## V1.3.2 适配器契约

银行侧适配器只允许以下能力：

| 能力 | 方法 | 外部路径 | 冻结要求 |
| --- | --- | --- | --- |
| 创建 Link | POST | `/api/links` | 银行侧携带稳定 `Idempotency-Key` 并按现有策略重试；V1.3.2 Core 不保证同 Key 去重，重复 Link 属于已知风险 |
| 查询 Link | GET | `/api/links/{id}` | 只保存和返回 Link UUID 及已批准字段；不读取外部表 |
| 查询点击分析 | GET | `/api/analytics/links/{id}?days={n}` | V1.3.2 只通过 API 读取 Core 已提供的点击分析；安装/App 聚合接口未确认时返回数据源不可用 |

安装/App 事件聚合的逐项核验记录见
[X-ANL-004：LinkForty 安装/App API 契约核验报告](./linkforty-analytics-contract-evidence.md)。V1.3.2 已明确不纳入安装/App 聚合成功能力，`installCount`/`inAppCount` 仅保留兼容字段；Core 的 SDK 写入接口和数据库字段不构成银行侧聚合读取契约，后续版本重新评估。

创建请求的重试规则固定为：4xx 不重试；429、5xx、连接超时按指数退避，最多 3 次；TLS、ACL、DNS 和证书错误不盲目重试。每次调用记录 `trace_id`、外部请求 ID、状态和耗时，不把凭据或完整敏感响应写入日志。

当前 Core 路由虽存在上述路径，但不读取 `Idempotency-Key`；银行侧保留稳定 Key 转发、错误分类和重试测试，并记录真实重复创建缺陷。该缺陷不在 V1.3.2 修复，也不标记为幂等验收通过；正式字段、TLS/ACL 和只读边界仍需外部证据。

## 集成规则

- 统一由 `LinkFortyClient` 封装。
- 外部调用必须设置超时。
- 外部成功、失败、重试和补偿结果必须通过 `trace_id`、任务日志和 M1 的 `operation_logs` 追踪，不在 Payload 中保存外部同步状态。
- 不允许业务模块直接拼装 HTTP 请求。
- 不允许直接修改 LinkForty 表。
- V1.3.2 不配置或使用 `bank_linkforty_ro`；数据库只读账号、SQL 授权和负向测试延期至 V1.4。

## 仍待确认的正式契约

- 创建 Link 正式请求/响应字段（基线路径为 `/api/links`）；
- 查询 Link 正式请求/响应字段（基线路径为 `/api/links/{id}`）；
- 错误响应格式；
- 限流和稳定幂等行为；
- 超时、TLS/ACL/DNS 错误分类和重试规则；
- 缓存失效规则。

## 字段映射

| 银行字段 | LinkForty 字段 | 备注 |
|---|---|---|
| `touchpoint_payloads.linkforty_link_id` | `links.id` | 外部 UUID 逻辑引用，不建立跨库外键 |

Payload 保存 NFC 卡内实际写入内容，不代表最终目标资源或路由配置。

本文件的网络隔离方案不替代银行后台面向浏览器 API 的 BFF Session Cookie 认证，也不替代 FastAPI 服务端验证 Casdoor OIDC/JWT 或 LinkForty Webhook 的 HMAC 签名验证。
