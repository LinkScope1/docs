# LinkForty API 集成契约

## 状态

网络访问方式已确定；LinkForty 平台正式路径、字段、错误和幂等契约仍待平台负责人确认。

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

## 集成规则

- 统一由 `LinkFortyClient` 封装。
- 外部调用必须设置超时。
- 外部成功、失败、重试和补偿结果必须通过 `trace_id`、任务日志和 M1 的 `operation_logs` 追踪，不在 Payload 中保存外部同步状态。
- 不允许业务模块直接拼装 HTTP 请求。
- 不允许直接修改 LinkForty 表。

## 仍待确认的正式契约

- 创建 Link 路径；
- 查询 Link 路径；
- 请求和响应字段；
- 错误响应格式；
- 限流和幂等行为；
- 超时和重试规则；
- 缓存失效规则。

## 字段映射

| 银行字段 | LinkForty 字段 | 备注 |
|---|---|---|
| `touchpoint_payloads.linkforty_link_id` | `links.id` | 外部 UUID 逻辑引用，不建立跨库外键 |

Payload 保存 NFC 卡内实际写入内容，不代表最终目标资源或路由配置。

本文件的网络隔离方案不替代银行后台面向浏览器 API 的 Casdoor JWT，也不替代 LinkForty Webhook 的 HMAC 签名验证。
