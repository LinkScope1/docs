# V1.3.2 权限矩阵

Casdoor 提供角色和功能权限；银行后台不创建本地 IAM 表。后端根据当前员工、Casdoor 权限集合以及业务表的 `org_id`、`employee_id` 强制执行数据范围。

## 角色×能力矩阵

| 能力 | 总行管理员 | 机构管理员 | 员工 | 观察者 | 范围 |
|---|---|---|---|---|---|
| 查询组织 | 允许 | 允许 | 允许 | 允许 | 总行 `GLOBAL`；机构 `ORG_SUBTREE`；员工 `ORG_SELF`；观察者 `ORG_SUBTREE` |
| 管理组织 | 允许 | 允许 | 禁止 | 禁止 | `organization.manage` + `ORG_SUBTREE` |
| 查询员工 | 允许 | 允许 | 允许 | 允许 | `ORG_SUBTREE`；员工默认 `ORG_SELF` |
| 管理员工 | 允许 | 允许 | 禁止 | 禁止 | `employee.manage` + `ORG_SUBTREE` |
| 物理删除员工 | 允许 | 允许 | 禁止 | 禁止 | 独立 `employee.delete` + `ORG_SUBTREE`；仅已停用且无当前绑定、责任或员工写入任务，禁止自删除 |
| 员工调动 | 允许 | 允许（来源、目标均为 `ORG_SUBTREE`） | 禁止 | 禁止 | `employee.transfer` + `SOURCE_AND_TARGET_ORG` |
| 查询触点资产 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 管理触点资产 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.asset.manage` |
| 永久作废资产 | 允许 | 允许（目标资产在 `ASSET_SCOPE`） | 禁止 | 禁止 | `touchpoint.asset.scrap` + `ASSET_SCOPE` |
| 查询载体内容 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 管理载体内容 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.payload.manage` |
| 查询地址页面 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.address-page.read` + `ORG_SUBTREE` |
| 管理地址页面 | 允许 | 允许 | 仅本机构/本人责任范围 | 禁止 | `touchpoint.address-page.manage` + `ORG_SUBTREE`；根组织页面可供下级资产使用；目标重新应用任务由后端按页面和资产组织范围生成，仍需 Core API 调用审计 |
| 物理删除地址页面 | 允许 | 允许 | 禁止 | 禁止 | 独立 `touchpoint.address-page.delete` + `ORG_SUBTREE`；仅已停用且无 queued/running 重新应用任务 |
| 在载体内容中选择地址页面或切换目标 | 允许 | 允许 | 资产可管理且地址页面责任组织可使用 | 禁止 | 同时校验 `touchpoint.payload.manage`、`touchpoint.asset.manage`、`touchpoint.address-page.read`；还需有效 `linkforty_link_id` 才能实时切换 |
| 查询绑定历史 | 允许 | 允许 | 允许 | 允许 | `ASSET_SCOPE` |
| 绑定/解绑 | 允许 | 允许（同组织 `ORG_SUBTREE`） | 仅同组织 `ORG_SELF` | 禁止 | `touchpoint.assignment.manage` |
| 跨组织转交 | 允许（需 `touchpoint.assignment.transfer`） | 允许（需 `touchpoint.assignment.transfer`） | 禁止 | 禁止 | `SOURCE_AND_TARGET_ORG` |
| 查询访问事件 | 允许 | 允许 | 允许 | 允许 | 机构 `ORG_SUBTREE`；员工 `EMPLOYEE_SELF`；观察者 `ORG_SUBTREE` |
| 统计查询 | 允许 | 允许 | 允许 | 允许 | 总行 `GLOBAL`；机构 `ORG_SUBTREE`；员工 `EMPLOYEE_SELF`；观察者 `ORG_SUBTREE` |
| 导入预校验 | 允许 | 允许 | 允许 | 禁止 | `ORG_SUBTREE`/`ASSET_SCOPE`，仅校验不写表 |
| 执行卡片、载体内容、员工导入 | 允许 | 允许 | 允许 | 禁止 | `import.validate` + 对应业务管理权限；每次执行必须携带 `Idempotency-Key` |
| 执行地址页面导入 | 允许 | 允许 | 允许 | 禁止 | `import.validate` + `touchpoint.address-page.manage`；缺失行不触发停用或删除 |
| 同步导出 | 允许 | 允许 | 禁止 | 禁止 | `ORG_SUBTREE`/`ASSET_SCOPE` + 字段白名单 |
| 载体内容原值导出 | 允许 | 按需授权 | 禁止 | 禁止 | `export.read` + `export.payload-content`，二次确认 |
| 查询操作审计 | 允许 | 允许 | 禁止 | 禁止 | `ORG_SUBTREE` |

## 权限执行规则

- Casdoor 角色和权限集合不复制到本地表。
- 前端菜单、路由和按钮只用于体验，不能替代后端校验。
- 物理删除是高风险独立权限；拥有 `employee.manage` 或 `touchpoint.address-page.manage` 不自动获得对应 delete 权限。
- 请求中的 `orgId`、`employeeId`、筛选条件只能缩小范围，不能扩大范围。
- 权限缺失和数据范围越界分别返回 `PERMISSION_DENIED` 和 `DATA_SCOPE_DENIED`。
- 员工列表的 `associatedCardCount` 只有在调用方同时具备 `employee.read`、
  `touchpoint.assignment.read` 和 `touchpoint.asset.read` 时才按资产范围聚合；
  缺少后两者时返回 `null`，不得伪装为 `0`。关联卡详情接口除 `employee.read` 外，
  还必须后端校验后两项读取权限，权限不足返回 `403`。
- 员工状态必须为正常、所属组织必须启用，才可获取业务访问上下文。
- 观察者只读，不能执行管理、绑定、导入、导出或审计查询。
- 重新应用任务查询使用 `touchpoint.address-page.read`；重试使用 `touchpoint.address-page.manage`。
  Service 必须重新读取页面组织并验证任务的页面关系、当前 `page_config_hash` 和调用方范围；
  Worker 不接受客户端资产列表或 Link ID，Payload 应用前再次验证资产、Payload、页面的组织层级关系。
  地址页面普通查询仍按页面组织范围过滤；资产选择/切换时允许启用的上级组织页面，前提是
  页面组织是该资产责任组织的祖先、调用方同时具备地址页面读取权限和资产/Payload 管理权限，
  且不因此授予下级用户修改上级页面的权限。
- 员工物理删除由 Service 在员工行锁内检查停用状态、当前绑定、资产/载体内容责任、正在执行的员工关系写入任务和自删除条件；地址页面物理删除由 Service 在页面行锁内检查停用状态和 queued/running 任务。两类删除都必须携带 `Idempotency-Key`、`confirm=true` 和非空 `reason`。

## 权限码与前端标识

Casdoor 权限码和前端 `data-testid` 是独立字段。权限码以 [权限与 API 映射](../03-api/permission-api-mapping.md) 为唯一项目内映射来源；本矩阵是本地冻结契约，Casdoor 正式导出是外部配置验收证据。
