# V1.3.2 权限矩阵

Casdoor 提供角色和功能权限；银行后台不创建本地 IAM 表。后端根据当前员工、Casdoor 权限集合以及业务表的 `org_id`、`employee_id` 强制执行数据范围。

## 角色×能力矩阵

| 能力 | 总行管理员 | 机构管理员 | 员工 | 观察者 | 范围 |
|---|---|---|---|---|---|
| 查询组织 | 允许 | 允许 | 允许 | 允许 | 总行 `GLOBAL`；机构 `ORG_SUBTREE`；员工 `ORG_SELF`；观察者 `ORG_SUBTREE` |
| 管理组织 | 允许 | 允许 | 禁止 | 禁止 | `organization.manage` + `ORG_SUBTREE` |
| 查询员工 | 允许 | 允许 | 允许 | 允许 | `ORG_SUBTREE`；员工默认 `ORG_SELF` |
| 管理员工 | 允许 | 允许 | 禁止 | 禁止 | `employee.manage` + `ORG_SUBTREE` |
| 员工调动 | 允许 | 允许（来源、目标均为 `ORG_SUBTREE`） | 禁止 | 禁止 | `employee.transfer` + `SOURCE_AND_TARGET_ORG` |
| 查询触点资产 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 管理触点资产 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.asset.manage` |
| 永久作废资产 | 允许 | 允许（目标资产在 `ASSET_SCOPE`） | 禁止 | 禁止 | `touchpoint.asset.scrap` + `ASSET_SCOPE` |
| 查询载体内容 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 管理载体内容 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.payload.manage` |
| 查询绑定历史 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 绑定/解绑 | 允许 | 允许（同组织 `ORG_SUBTREE`） | 仅同组织 `ORG_SELF` | 禁止 | `touchpoint.assignment.manage` |
| 跨组织转交 | 允许（需 `touchpoint.assignment.transfer`） | 允许（需 `touchpoint.assignment.transfer`） | 禁止 | 禁止 | `SOURCE_AND_TARGET_ORG` |
| 查询访问事件 | 允许 | 允许 | 允许 | 允许 | 机构 `ORG_SUBTREE`；员工 `EMPLOYEE_SELF`；观察者 `ORG_SUBTREE` |
| 统计查询 | 允许 | 允许 | 允许 | 允许 | 总行 `GLOBAL`；机构 `ORG_SUBTREE`；员工 `EMPLOYEE_SELF`；观察者 `ORG_SUBTREE` |
| 导入预校验 | 允许 | 允许 | 允许 | 禁止 | `ORG_SUBTREE`/`ASSET_SCOPE`，仅校验不写表 |
| 同步导出 | 允许 | 允许 | 禁止 | 禁止 | `ORG_SUBTREE`/`ASSET_SCOPE` + 字段白名单 |
| 查询操作审计 | 允许 | 允许 | 禁止 | 禁止 | `ORG_SUBTREE` |

## 权限执行规则

- Casdoor 角色和权限集合不复制到本地表。
- 前端菜单、路由和按钮只用于体验，不能替代后端校验。
- 请求中的 `orgId`、`employeeId`、筛选条件只能缩小范围，不能扩大范围。
- 权限缺失和数据范围越界分别返回 `PERMISSION_DENIED` 和 `DATA_SCOPE_DENIED`。
- 员工状态必须为正常、所属组织必须启用，才可获取业务访问上下文。
- 观察者只读，不能执行管理、绑定、导入、导出或审计查询。

## 权限码与前端标识

Casdoor 权限码和前端 `data-testid` 是独立字段。权限码以 [权限与 API 映射](../03-api/permission-api-mapping.md) 为唯一项目内映射来源；本矩阵是本地冻结契约，Casdoor 正式导出是外部配置验收证据。
