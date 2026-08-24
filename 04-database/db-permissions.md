# 数据库权限方案

## 账号

| 账号 | 权限 |
|---|---|
| bank_admin_rw | 银行业务 Schema 读写 |
| bank_linkforty_ro | 指定 LinkForty 表只读 |
| bank_migration | 银行业务 Schema 迁移 |

## 运行与迁移分离

- `bank_admin_rw` 只用于银行 API/Worker 运行，不能拥有 DDL、创建扩展、`TRUNCATE` 或执行 Alembic。
- `bank_migration` 只在受审批的发布作业中使用，负责 `bank_admin` Schema 的 Alembic upgrade；测试迁移账号与生产迁移账号分离。
- 生产数据库连接、迁移连接和 `bank_linkforty_ro` 凭据不得写入仓库、日志或审计详情。
- 本地迁移验证使用临时数据库或离线 SQL；不得从银行迁移脚本修改 LinkForty 表。

## LinkForty 只读边界

- M5：只读 `links`、`click_events` 的必要字段，用于访问事件接入与关联。
- 非编号统计与报表能力：只读 `links`、`click_events`、`device_fingerprints`、`install_events`、`in_app_events` 的必要字段，不拥有本地专属表。
- `webhooks`、`webhook_deliveries` 默认不授予读取权限；`bank_linkforty_ro` 永远不得读取 `webhooks.secret`。Webhook Secret provisioning 通过受控 Core API 完成，不改变数据库表、字段或只读账号授权。
- 只读账号默认拒绝未列入白名单的表、字段和任何 LinkForty 写操作。
- 禁止 LinkForty DML、DDL 和 TRUNCATE。
- 所有权限变更必须经过审批并记录。
- 隔离测试库的授权脚本见银行后台仓库 `database/checks/linkforty_readonly_permissions.sql`；负向测试必须由 DBA 在 LinkForty 测试/预发布库实际执行，不能用本地 Mock 代替。
