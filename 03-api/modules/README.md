# M1–M5 API 模块契约

本目录按业务模块维护 OpenAPI Path Item 片段，系统总入口仍为 [`../openapi.yaml`](../openapi.yaml)。模块文件不是第二套完整 OpenAPI 文档，不得重复定义全局响应、错误码、分页或安全方案。

## 文件分工

| 文件 | 模块 | 范围 |
| --- | --- | --- |
| `m1-auth-audit.yaml` | M1 | 当前访问上下文、操作日志查询 |
| `m2-organizations.yaml` | M2 | 组织增查改、启停 |
| `m2-employees.yaml` | M2 | 员工增查改、启停、调动 |
| `m3-assets.yaml` | M3 | NFC资产增查改、启停、作废 |
| `m3-payloads.yaml` | M3 | 载体内容增查改、启停、失效 |
| `m4-assignments.yaml` | M4 | 绑定、解绑、转交和历史查询 |
| `m5-access-events.yaml` | M5 | 访问事件接入、查询和关联处理 |

## 必须标注的内容

每个接口至少维护以下扩展字段：

- `x-status`：`planned`、`reviewed`、`implemented`或`deprecated`。
- `x-owner`：负责人；未分配时使用`待确认`。
- `x-permission`：所需功能权限。
- `x-data-scope`：`org_id`、`employee_id`或系统级范围。
- `x-idempotency`：是否要求`Idempotency-Key`。
- `x-audit`：是否写入`operation_logs`。

## 修改流程

1. 开发前补齐对应模块文件中的请求、响应和业务约束，将状态改为`reviewed`。
2. 在总入口`openapi.yaml`的具体路径中通过`$ref`引用对应Path Item。
3. 实现后端、测试并完成联调后，将状态改为`implemented`。
4. 接口字段变化必须在同一PR同步修改模块契约和总入口。

> OpenAPI标准不能自动合并多个完整的`paths`对象。总入口必须逐个路径引用模块文件中的具名Path Item，不能把这些文件当作互相独立的完整API。
