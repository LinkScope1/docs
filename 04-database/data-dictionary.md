# 数据字典

## 本系统 16 张表

| 序号 | 表 | 归属模块 | 用途 |
|---:|---|---|---|
| 1 | organization_units | M2 | 组织树 |
| 2 | customer_managers | M2 | 客户经理 |
| 3 | touchpoint_assets | M3 | NFC 资产 |
| 4 | target_resources | M5 | 目标资源 |
| 5 | touchpoint_payloads | M3 | 载体写入内容 |
| 6 | touchpoint_manager_assignments | M4 | 绑定历史 |
| 7 | routing_rules | M6 | 路由规则和发布状态 |
| 8 | access_events | M7 | 访问事件投影 |
| 9 | iam_users | M1 | Casdoor 主体映射 |
| 10 | iam_user_organizations | M1 | 用户组织归属 |
| 11 | iam_roles | M1 | 角色投影 |
| 12 | iam_permissions | M1 | 权限资源 |
| 13 | iam_permission_apis | M1 | 权限到 API 映射 |
| 14 | iam_role_permissions | M1 | 角色权限关系 |
| 15 | iam_user_role_scopes | M1 | 角色数据范围 |
| 16 | operation_logs | M1 | 操作审计 |

## 必须单独确认的字段

- 所有业务表的 BIGINT ID。
- 组织和人员编码唯一性。
- 资产 UID 唯一性。
- `target_resources` 的二选一约束。
- 绑定时间区间约束。
- 路由规则冲突约束。
- `access_events.event_id` 唯一约束。
