# LinkForty API 集成契约

## 状态

网络访问方式已确定；本地 Core 代码可观察到 `POST /api/links` 和
`GET /api/links/:id`，但正式字段、错误和网络安全边界仍必须由平台负责人以接口样例确认。Core 当前不执行 `Idempotency-Key` 服务端去重；同 Key 重复创建是 V1.3.2 已知限制。

## 调用安全边界

银行后台通过 Nginx 的 `/linkapi/` 反向代理调用 LinkForty Core，不允许银行后台绕过该代理直连 Core。

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

## Nginx 代理路径

银行后台的 `LINKFORTY_BASE_URL` 是 Nginx 的代理前缀，例如
`https://links.example.com/linkapi`，Client 在其后拼接 Core API 路径。Nginx 必须使用带
末尾 `/` 的 Core `proxy_pass`，以移除 `/linkapi` 前缀：

| 银行侧请求 | Core 实际请求 |
| --- | --- |
| `/linkapi/api/links` | `/api/links` |
| `/linkapi/api/analytics/*` | `/api/analytics/*` |
| `/linkapi/<short_code>` | `/<short_code>` |

当前测试配置为宿主机 Nginx：`proxy_pass http://127.0.0.1:3200/;`。只有在 Nginx 与 Core
加入同一 Docker 网络时，才可使用已确认的 Core Compose 服务名和容器端口：
`proxy_pass http://linkforty:3000/;`。当前 Core 与银行测试 Compose 默认网络隔离，不能
直接将 `linkforty:3000` 作为跨 Compose 地址。

Nginx 只作为受控网络边界，不改变请求方法、请求体或 `Idempotency-Key`，并对 Core API
关闭代理缓存。Core API 端口仍绑定私有地址，不得公网暴露。

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
| 更新 Link 目标 | PUT | `/api/links/{id}` | 仅更新同一 Link 的 `originalUrl`/`webFallbackUrl`；网页和小程序直接提交目标，APP 提交 `card-switch-demo` Bridge URL；不添加 Core 未声明支持的幂等请求头 |
| 查询点击分析 | GET | `/api/analytics/links/{id}?days={n}` | V1.3.2 只通过 API 读取 Core 已提供的点击分析；安装/App 聚合接口未确认时返回数据源不可用 |

安装/App 事件聚合的逐项核验记录见
[X-ANL-004：LinkForty 安装/App API 契约核验报告](./linkforty-analytics-contract-evidence.md)。V1.3.2 已明确不纳入安装/App 聚合成功能力，`installCount`/`inAppCount` 仅保留兼容字段；Core 的 SDK 写入接口和数据库字段不构成银行侧聚合读取契约，后续版本重新评估。

创建请求的重试规则固定为：4xx 不重试；429、5xx、连接超时按指数退避，最多 3 次；TLS、ACL、DNS 和证书错误不盲目重试。每次调用记录 `trace_id`、外部请求 ID、状态和耗时，不把凭据或完整敏感响应写入日志。Nginx 的 502/504 仍按网络或上游不可用分类处理。

当前 Core 路由虽存在上述路径，但不读取 `Idempotency-Key`；银行侧保留稳定 Key 转发、错误分类和重试测试，并记录真实重复创建缺陷。目标更新使用同 Link ID + 同目标的逻辑幂等：重复请求先读取外部目标，目标相同则银行返回 `NO_CHANGE`，不重复调用 Core。该缺陷不在 V1.3.2 修复，也不标记为幂等验收通过；正式字段、TLS/ACL 和只读边界仍需外部证据。

## M3 地址页面目标切换

银行后台入口为 `POST /api/v1/touchpoint-payloads/{id}/switch-address-page`。地址页面
`PATCH /api/v1/touchpoint-address-pages/{id}` 只更新银行地址页面和审计；目标配置发生变化时，
事务提交后创建地址页面重新应用任务，再由 Worker 对任务明细逐条调用同一应用 Service。
网页（`content_type=3`）和小程序（`content_type=1`）直接使用目标；小程序的目标必须是公开
HTTPS Universal Link，业务库不要求通用 URL 格式，但 Core 校验失败必须原样归类为失败。APP
（`content_type=2`）由银行侧使用 `metadata.app` 和 `TOUCHPOINT_APP_BRIDGE_BASE_URL`
生成 `app-open.html` URL；不得把 APP Scheme 直接提交给 Core。地址页面表不保存绑定具体 Link
ID 的最终 Bridge URL，历史占位 Bridge URL 仅在解析器中兼容。

目标切换始终保留 NFC 实际写入的 `payload_value` 和 `linkforty_link_id`。更新前通过 `GET /api/links/{id}` 校验 Core 目标与银行 `target_url` 快照一致；每个 Payload 独立处理，不使用客户端提供的资产或 Link ID。Core 更新成功后才落银行快照，银行事务失败、后续 Core 更新失败或批量失败时使用旧目标补偿，并通过 `trace_id` 和 `operation_logs` 记录成功、失败、冲突与补偿结果。Core 与银行库不组成分布式事务，因此该流程提供补偿意义上的最终一致，而非原子事务。

### 新建 Payload 选择地址页面

`POST /api/v1/touchpoint-assets/{assetId}/payloads` 只接收路径中的资产 ID、`payloadType`、
`payloadSource`、`providerType`、`addressPageId` 和非敏感 metadata。选择地址页面时不接收
`linkfortyLinkId`，也不要求客户端生成 `payloadValue`。银行侧先使用占位 `linkId` 创建 LinkForty
Link，取得真实 UUID 后通过同一个 `PUT` 替换为最终目标；LinkForty 返回的短链作为新的
`payload_value` 保存。创建 Link 后银行本地落库失败时只通过 LinkForty API 删除新 Link。

### App Bridge 与公开中间页

`TOUCHPOINT_APP_BRIDGE_BASE_URL` 必须是公开 HTTPS 静态站点上的 `app-open.html` 绝对地址，
例如 `https://links.example.com/app-open.html`。银行后端不执行 `app.js` 或 `app-open.js`，
只在 `app_bridge.py` 中按既有协议生成 URL；浏览器/移动端打开该静态页后才执行中间页逻辑。
生成的查询参数为：

| Bridge 参数 | 来源 |
| --- | --- |
| `iosScheme` | `metadata.app.iosScheme` |
| `androidScheme` | `metadata.app.androidScheme` |
| `harmonyScheme` | `metadata.app.harmonyScheme` |
| `appPayload` | `metadata.app.appPayload` |
| `linkId` | LinkForty 返回的真实 Link UUID |
| `defaultPage` | `metadata.app.webFallbackUrl` |

新建 Link 时允许短暂使用 `__LINK_ID__` 占位目标，取得真实 UUID 后必须 PUT 回同一个 Link；
后端不会把最终 Bridge URL 写入地址页面主数据。解析器只为历史占位 Bridge URL 提供兼容替换，
不会执行演示仓库代码。App Scheme、Payload 和回退地址的变更会参与页面配置 hash，并触发
绑定 Payload 的重新应用任务。

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
