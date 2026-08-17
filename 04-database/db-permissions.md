# 数据库权限方案

## 账号

| 账号 | 权限 |
|---|---|
| bank_admin_rw | 银行业务 Schema 读写 |
| bank_linkforty_ro | 指定 LinkForty 表只读 |
| bank_migration | 银行业务 Schema 迁移 |

## LinkForty 只读边界

- M7：只读 `links`、`click_events` 必要字段。
- M8：只读 `click_events`、`device_fingerprints`、`install_events`、`in_app_events` 和必要 Link 字段。
- 禁止读取 `webhooks.secret`。
- 禁止 LinkForty DML、DDL 和 TRUNCATE。
- 所有权限变更必须经过审批并记录。
