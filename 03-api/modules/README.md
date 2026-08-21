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

- `x-status`：`planned`、`reviewed`、`implemented`或`deprecated`。V1.3.2 冻结接口使用 `reviewed`；这不表示业务代码已实现。
- `x-owner`：负责人或负责岗位；外部负责人尚未确认时必须在冻结证据中列为待补证，不得伪造个人签字。
- `x-permission`：所需功能权限。
- `x-data-scope`：`GLOBAL`、`ORG_SUBTREE`、`ORG_SELF`、`EMPLOYEE_SELF`、`ASSET_SCOPE`、`SOURCE_AND_TARGET_ORG`或`SYSTEM`。
- `x-idempotency`：V1.3.2 的领域幂等策略；通用响应回放延期到 V1.4。
- `x-audit`：是否写入`operation_logs`。

## 修改流程

1. 开发前补齐对应模块文件中的请求、响应和业务约束，将状态改为`reviewed`。
2. 在总入口`openapi.yaml`的具体路径中通过`$ref`引用对应Path Item。
3. 实现后端、测试并完成联调后，将状态改为`implemented`。
4. 接口字段变化必须在同一PR同步修改模块契约和总入口。

> OpenAPI标准不能自动合并多个完整的`paths`对象。总入口必须逐个路径引用模块文件中的具名Path Item，不能把这些文件当作互相独立的完整API。
