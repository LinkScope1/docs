# 审计规范

## 必须审计

- 登录和身份同步。
- 创建、修改、启停和作废。
- 批量导入。
- 绑定、解绑和转交。
- 目标资源修改。
- 路由规则发布。
- LinkForty 外部调用结果。
- 访问事件重试。
- 数据导出。
- 权限和数据范围变更。

## 审计字段

- `trace_id`
- `operator_id`
- `scope_org_id`
- `operation_type`
- `object_type`
- `object_id`
- `operation_result`
- `operation_summary`
- `before_data`
- `after_data`
- `error_code`
- `operation_time`

审计日志只追加，普通业务用户不可修改或删除。
