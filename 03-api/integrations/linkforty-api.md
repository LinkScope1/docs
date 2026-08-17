# LinkForty API 集成契约

## 状态

待 LinkForty 平台负责人提供正式契约。

## 需要覆盖

- 创建 Link。
- 查询 Link。
- 修改 Link 目标配置。
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
- 外部失败必须记录本地状态和操作日志。
- 不允许业务模块直接拼装 HTTP 请求。
- 不允许直接修改 LinkForty 表。

## 字段映射

| 银行资源 | LinkForty 字段 | 备注 |
|---|---|---|
| 短链 | `link_id` | 外部 UUID 引用 |
| 长链 | `resource_value` | 映射为目标 URL |
| App 包名 | `resource_value` + metadata | 需要确认平台字段 |
| 入口 Link | Payload 内容 | 不等同最终目标 |
