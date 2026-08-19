# 数据库权限方案

## 账号

| 账号 | 权限 |
|---|---|
| bank_admin_rw | 银行业务 Schema 读写 |
| bank_linkforty_ro | 指定 LinkForty 表只读 |
| bank_migration | 银行业务 Schema 迁移 |

## LinkForty 只读边界

- M5：只读 `links`、`click_events` 的必要字段，用于访问事件接入与关联。
- 非编号统计与报表能力：只读 `links`、`click_events`、`device_fingerprints`、`install_events`、`in_app_events` 的必要字段，不拥有本地专属表。
- `webhooks`、`webhook_deliveries` 默认不授予读取权限；如后续确需读取，必须单独审批字段白名单，且永远不得读取或输出 `webhooks.secret`。
- 只读账号默认拒绝未列入白名单的表、字段和任何 LinkForty 写操作。
- 禁止 LinkForty DML、DDL 和 TRUNCATE。
- 所有权限变更必须经过审批并记录。
