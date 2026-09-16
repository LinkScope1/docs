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

审计查询响应可以根据 `employee_id` 在读取时解析 `employee_code` 和 `employee_name`；员工已物理删除时，使用 `deleted_employees` 的归档快照。姓名不复制到 `operation_logs`，该展示不保证还原操作发生时的姓名。审计查询须通过 `audit.read`，审计日志导出须通过 `export.read`，两者都必须遵守已授权数据范围。

`operationTypeLabel` 是展示字段，不是持久化列。由于现有调用点对部分 `operation_type` 编号存在复用，标签须结合对象类型和安全摘要生成；未知编号必须显示明确回退值。不要仅凭数值编号在前端重新解释操作语义。
