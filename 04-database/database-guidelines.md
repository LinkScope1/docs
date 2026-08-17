# 数据库规范

## 基本规则

- 数据库使用 PostgreSQL 14+。
- 银行业务表使用 `bank_admin` Schema。
- 迁移使用 Alembic。
- BIGINT 主键通过 API 以字符串传输。
- PostgreSQL UUID 保留 UUID 类型。
- 时间字段使用带时区类型。
- `access_events` 不分区。
- `event_id` 全局唯一。
- `click_id` 只建普通索引。
- JSONB 只用于低频扩展属性。

## 表和字段

- 表名和字段名使用 snake_case。
- 状态字段必须有文档定义。
- 创建和修改时间统一命名。
- 创建人和修改人使用逻辑引用。
- 历史快照字段不能依赖主数据级联删除。

## 迁移

- 每个数据库变更必须有 Alembic revision。
- 迁移必须可重复检查。
- 生产迁移前必须备份。
- 大表变更必须评估锁和耗时。
- 不允许通过应用启动时静默修改生产表。
