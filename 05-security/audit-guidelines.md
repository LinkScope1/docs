# 审计规范

## 必须审计

- 登录和认证上下文校验。
- 创建、修改、启停和作废。
- 批量导入。
- 绑定、解绑和转交。
- 载体内容修改和外部同步。
- 文档导入和绑定关系变更。
- LinkForty 外部调用结果。
- 访问事件重试。
- 数据导出。
- 权限和数据范围变更。

## 审计字段

- `trace_id`
- `org_id`
- `employee_id`
- `operation_type`
- `object_type`
- `object_id`
- `external_object_id`
- `operation_result`
- `operation_summary`
- `operation_detail`
- `before_data`
- `after_data`
- `error_code`
- `error_message`
- `operation_time`

审计日志只追加，普通业务用户不可修改或删除。
