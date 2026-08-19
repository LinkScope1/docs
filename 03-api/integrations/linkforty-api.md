# LinkForty API 集成契约

## 状态

待 LinkForty 平台负责人提供正式契约。

## 需要覆盖

- 创建 Link。
- 查询 Link。
- 查询点击事实。
- API 认证。
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

## 字段映射

| 银行字段 | LinkForty 字段 | 备注 |
|---|---|---|
| `touchpoint_payloads.linkforty_link_id` | `links.id` | 外部 UUID 逻辑引用，不建立跨库外键 |

Payload 保存 NFC 卡内实际写入内容，不代表最终目标资源或路由配置。
