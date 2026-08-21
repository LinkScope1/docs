# LinkForty API 集成契约

## 状态

网络访问方式已确定；本地 Core 代码可观察到 `POST /api/links` 和
`GET /api/links/:id`，但正式字段、错误和幂等能力仍必须由平台负责人以接口样例确认。

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
- 查询点击事实。
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
| 创建 Link | POST | `/api/links` | 必须携带稳定 `Idempotency-Key`；同 Key 同 Payload 返回首次结果，同 Key 不同 Payload 返回冲突 |
| 查询 Link | GET | `/api/links/{id}` | 只保存和返回 Link UUID 及已批准字段；不读取外部表 |

创建请求的重试规则固定为：4xx 不重试；429、5xx、连接超时按指数退避，最多 3 次；TLS、ACL、DNS 和证书错误不盲目重试。每次调用记录 `trace_id`、外部请求 ID、状态和耗时，不把凭据或完整敏感响应写入日志。

当前 Core 路由虽存在上述路径，但尚未提供本文件要求的稳定幂等证据；在平台补齐 Header/等价服务端语义并完成重复、并发、429、5xx、超时测试前，`P0-LF-001/002` 保持阻塞。

## 集成规则

- 统一由 `LinkFortyClient` 封装。
- 外部调用必须设置超时。
- 外部成功、失败、重试和补偿结果必须通过 `trace_id`、任务日志和 M1 的 `operation_logs` 追踪，不在 Payload 中保存外部同步状态。
- 不允许业务模块直接拼装 HTTP 请求。
- 不允许直接修改 LinkForty 表。

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

本文件的网络隔离方案不替代银行后台面向浏览器 API 的 Casdoor JWT，也不替代 LinkForty Webhook 的 HMAC 签名验证。
