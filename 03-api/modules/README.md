# M1–M5 API 模块契约

本目录按业务模块维护 OpenAPI Path Item 评审镜像，系统总入口仍为 [`../openapi.yaml`](../openapi.yaml)，且总入口是唯一机器源。模块文件不是第二套完整 OpenAPI 文档，不得重复定义全局响应、错误码、分页或安全方案。

每个模块 Path Item 使用 `x-canonical-path` 标识总入口路径，操作使用与总入口一致的 `operationId`。CI 会校验模块镜像与总入口的路径、方法、权限、数据范围、幂等和审计元数据一致；模块文件可以使用空响应或不含 Schema 的状态/错误摘要作为评审镜像，但不是可单独发布的 OpenAPI 文档。

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
2. 在总入口 `openapi.yaml` 中维护完整机器契约，并同步更新对应模块评审镜像。
3. 实现后端、测试并完成联调后，将状态改为 `implemented`；`reviewed` 只表示契约已评审冻结，不表示业务代码已实现。
4. 接口字段变化必须在同一 PR 同步修改总入口和模块评审镜像。

> OpenAPI 标准不能自动合并多个完整的 `paths` 对象。V1.3.2 采用总入口机器源加模块评审镜像，CI 通过 `x-canonical-path` 和 `operationId` 保证两者不漂移；不把模块文件当作互相独立的完整 API。
