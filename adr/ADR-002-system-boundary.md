# ADR-002：银行后台与 LinkForty Core 分离

## 状态

Accepted

## 决策

银行后台作为独立 Python 服务建设，LinkForty Core 继续负责短链平台和原始事件。

## 规则

- 银行后台不直接修改 LinkForty 表。
- LinkForty 写入必须通过 API。
- M5 使用受限只读访问读取必要的 LinkForty 事件关联数据；非编号统计与报表能力只读获授权的事件数据。
- 只读账号遵循 `docs/04-database/db-permissions.md` 的表和字段白名单，不读取 `webhooks` 或 `webhooks.secret`；受控 Core API provisioning 是独立的配置交付路径。
- 前端只调用银行后台 API。
