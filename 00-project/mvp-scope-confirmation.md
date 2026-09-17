# V1.3.2 MVP 范围确认记录

## 记录信息

| 项目 | 内容 |
|---|---|
| 任务 ID | `P0-BASE-003` |
| 基线版本 | `V1.3.2` 数据模型、`V3.1` MVP 模块方案 |
| 确认日期 | 2026-08-20 |
| 确认状态 | 已确认 |
| 记录目的 | 冻结当前 MVP 范围，作为 Issue、API、数据库、前端和测试任务的越界判断依据 |
| 适用仓库 | `docs/`、`bank-touchpoint-backend/`、`bank-touchpoint-frontend/` |
| 不适用范围 | `linkforty/core/` 外部系统和 `card-switch-demo/` 演示项目不计入银行后台 MVP 完成度 |

本记录只确认范围，不代表 M1～M5 已经实现。目录、迁移、接口草稿、Mock 或静态页面仍须按代码、测试和运行证据分别判断完成状态。

## 一、纳入 V1.3.2 MVP

| 范围 | 纳入内容 | 边界和验收口径 |
|---|---|---|
| M1 | Casdoor OIDC BFF、`employee_code` 员工映射、权限和数据范围上下文、操作审计 | Casdoor 是身份、角色和功能权限权威；银行后台不创建本地 IAM 权限投影；浏览器只持有 HttpOnly Session Cookie，关键操作通过 `operation_logs` 审计 |
| M2 | 组织和员工管理 | 组织层级使用 `org_code` 前缀；员工使用唯一 `employee_code` 和直接所属 `org_id`；查询、写入和导出执行后端范围校验 |
| M3 | NFC 触点资产、可复用地址页面、载体实际内容、LinkForty 外部调用编排 | 一期 `asset_type` 固定为 NFC；地址页面按组织范围复用，`content_type` 为小程序/APP/网页，`target_url` 不强制 HTTP/HTTPS；Payload 是卡内实际写入内容，不是目标资源；LinkForty 写入必须通过 API |
| M4 | 触点载体与员工的立即生效绑定、解绑、转交和历史记录 | 绑定历史只追加；有效区间不得重叠；不保存组织或员工名称快照；预约绑定延期至 V1.4 |
| M5 | Webhook 验签、访问事件幂等投影、资产/绑定/组织/员工关联和失败重试 | `event_id` 全局唯一，`click_id` 非唯一；`access_events` 不分区；关联失败可进入重试或最终失败审计 |
| 横向：权限与审计 | 数据范围、操作审计、幂等、Trace ID、敏感信息脱敏 | 前端隐藏不能替代后端权限校验；不得记录 JWT、Token、密码、密钥或 Webhook Secret |
| 横向：统计与报表 | 点击、访问统计，以及同步导出；安装/App 统计字段保留兼容结构 | V1.3.2 只验收点击和访问统计；安装/App 聚合读取不纳入当前版本，相关字段保留但未支持时整体返回 `503 DATA_SOURCE_UNAVAILABLE`；统计不包含银行办理量、金额或真实业务转化；异步导出为 V1.4 |
| 横向：Worker | Webhook、LinkForty 外部调用和关联失败的重试、补偿和审计 | Worker 不是新的业务模块；Redis/Celery 不能作为唯一事实来源；结果通过 `operation_logs` 和 `trace_id` 追踪 |
| 横向：文档导入契约 | 载体内容、地址页面、载体员工绑定、载体内容关系模板，以及稳定匹配键、预校验和逐行结果 | 组织/员工沿用各自稳定键；Payload 和绑定关系使用 `cardId` 定位资产；资产模板只新增，不提供资产编码/卡ID且不匹配或更新既有资产，重复非空 UID 拒绝；缺少某行不推导删除、停用或解绑 |
| 外部依赖：LinkForty | API 写入、授权事件只读访问、Webhook 事件接入和受控 Secret provisioning | 只读账号只能访问白名单表和字段；银行后台不得直接执行 LinkForty DML、DDL 或 TRUNCATE；Secret 仅通过受控 Core API 一次性交付 |
| 外部依赖：NFC | NFC 适配器接口和明确的 Mock 流程 | 真实硬件写卡依赖硬件/SDK确认；没有真实设备时 Mock 不得伪造真实核验成功 |

## 二、不纳入本期或延期至后续版本

| 项目 | 判定 | 越界判断 |
|---|---|---|
| 本地 `iam_*` 表、角色和权限投影 | 不纳入 V1.3.2 | 需求若要求银行库复制 Casdoor 身份、角色或功能权限，直接判定越界 |
| `target_resources`、目标资源管理 | 不纳入 V1.3.2 | 不创建目标资源表、API、菜单、状态或目标资源业务流程 |
| `routing_rules`、路由配置和路由发布 | 不纳入 V1.3.2 | 不创建路由规则表，不实现路由发布、冲突处理、实时路由计算或目标资源二选一 |
| 二维码、条形码等其他介质完整流程 | 不纳入 V1.3.2 | 一期只支持 NFC；其他介质须另行进行版本和范围评审 |
| 银行业务办理量、办理金额和真实业务转化 | 不纳入 MVP 验收 | 访问、点击、安装和 App 事件不能被描述为银行业务办理结果 |
| 复杂审批流 | 不纳入 V1.3.2 | 绑定、解绑、转交不扩展为通用审批引擎或复杂多级审批流程 |
| 完整版本可视化回滚 | 不纳入 V1.3.2 | 不建设完整版本历史可视化和一键回滚能力 |
| 自动化 NFC 硬件写卡 | 条件能力，不作为软件 MVP 门槛 | 硬件和 SDK 未确认时只交付适配接口和 Mock；真实设备接入需独立确认和验收 |
| 导入批次表、导入明细表和完整异步导入 | 不纳入 V1.3.2 | 不新增导入专属持久化表或异步导入后台流程；契约预留不等于功能已实现 |
| 预约绑定 | 延期至 V1.4 | V1.3.2 只支持立即生效绑定，不根据请求时间隐式产生预约行为 |
| 安装/App 聚合读取 | 延期至 V1.4，重新评估 | V1.3.2 不实现 Core 安装/App 聚合 API 或银行侧聚合 Client；保留 `installCount`/`inAppCount` 兼容字段，必要能力不支持时整体返回 `503 DATA_SOURCE_UNAVAILABLE`，不直连数据库、不返回伪造零值或部分成功 |

## 三、系统边界与数据规则

- 银行后台只拥有 8 张银行业务表：`operation_logs`、`organization_units`、`employees`、`touchpoint_assets`、`touchpoint_payloads`、`touchpoint_address_pages`、`touchpoint_employee_assignments`、`access_events`。
- `touchpoint_address_pages` 的 `org_id` 是责任组织；`address_name` 是管理展示标识；`status` 为 0 停用/1 启用；地址页面被 Payload 使用后仍可在满足停用和任务校验后物理删除，但不得修改或清空既有 Payload，历史信息由删除归档快照解析。
- `touchpoint_payloads` 只保存卡内实际内容和必要的 `linkforty_link_id` 逻辑引用，不保存 LinkForty 专属同步状态、同步时间、错误摘要或重试次数。
- 银行后台对 LinkForty 的写入必须通过 API；读取外部事件只能使用受限只读账号；不得通过 LinkForty 数据库直读 `webhooks.secret`。当前方案允许银行后端配置服务通过受控 Core API 一次性 provisioning Secret；不得记录、前端暴露或输出 Secret。
- `event_id` 是访问事件全局唯一幂等键，`click_id` 只能作为非唯一逻辑引用；重复 `event_id` 必须幂等成功。
- 统计与报表不拥有本地专属事实表；银行业务办理量和金额不进入 MVP 正式验收。
- `linkforty/core/` 是独立外部系统，`card-switch-demo/` 是演示项目；两者的目录、页面或接口不能作为银行后台业务完成证据。

### DEC-LF-006：Webhook Secret provisioning

| 项目 | 决策 |
|---|---|
| 当前方案 | 沿用 Core 现有 `POST /api/webhooks` 创建响应获取 Secret；已存在订阅可受控调用 `GET /api/webhooks/:id` 一次性读取；不新增 provisioning API。 |
| 调用方 | 银行后端配置服务；前端、普通业务 API 和 LinkForty 数据库只读账号不参与。 |
| 运行时行为 | Secret 写入受保护运行时配置；Webhook 事件和重试由银行后台本地验签，不按事件调用 Core。 |
| 安全边界 | Core 管理 API 仅通过私有网络、来源 ACL、防火墙、私有 DNS、HTTPS/TLS 和网络审计访问；Secret 不进入银行业务表、日志、审计、fixture、文档或前端。 |
| 状态 | 方案已确认；配置服务联调、网络访问审计和生产配置接入仍待实施和验收。 |

## 四、影响分析

| 领域 | 本次范围结论 | 后续执行要求 |
|---|---|---|
| API | 只为 M1～M5 和已确认的横向能力定义或实现接口；不新增目标资源、路由、二维码或本地 IAM API | 新 Issue 必须标明 `V1.3.2`、`V1.4` 或条件任务，并关联对应模块或横向能力 |
| 数据库 | 只演进银行侧 8 张表及横向 `import_batches`；不创建 `iam_*`、`target_resources`、`routing_rules` 或导入明细表 | 数据结构变化使用新的银行侧 Alembic revision；不得修改 LinkForty 平台表 |
| 权限与数据范围 | Casdoor 提供角色和功能权限；银行后台按 `org_id`、`employee_id` 执行范围过滤 | 所有 API、导出、导入预留和后台命令都必须有后端权限与范围校验 |
| 外部集成 | LinkForty API、Webhook、受限只读和 NFC 适配属于外部/横向能力 | Casdoor、LinkForty、NFC 的未决契约分别保留 P0 外部确认依赖；未确认项不得被实现人员自行假定 |
| 测试与验收 | 验收覆盖 M1～M5、统计报表、范围校验、幂等、审计和导入契约预留 | 验收矩阵不得把不纳入项列为 V1.3.2 完成条件；Mock 不替代真实硬件验收结论 |
| 文档与协作 | 本记录作为 P0-BASE-003 的范围证据 | 范围变更必须更新本记录、任务清单和受影响的验收/契约资料，并重新评审 |

## 五、确认与变更规则

| 评审角色 | 确认事项 | 状态 |
|---|---|---|
| 产品负责人 | 纳入项、不纳入项、V1.4 延期项和 MVP 验收边界 | 已确认 |
| 架构师 | 银行后台、Casdoor、LinkForty、NFC 和演示项目的系统边界 | 已确认 |
| 后端/测试 | 范围可拆分为 M1～M5 和横向能力，且不将骨架误判为已实现 | 已确认 |
| Casdoor/LinkForty/NFC/DBA | 具体外部契约、账号、硬件和网络条件 | 仍按 P0 外部确认任务跟踪，不改变本范围记录 |

以下任何变化都必须重新评审并更新记录：增加新的业务介质、引入本地 IAM、增加目标资源或路由、改变事件幂等规则、增加银行办理量/金额、将 V1.4 能力提前到 V1.3.2，或扩大银行后台对 LinkForty 的数据库访问权限。

## 六、完成证据

- `P0-BASE-003` 状态更新为“已具备”，证据类型为“决策记录/范围确认”。
- `master-checklist.md` 中“确认 MVP 范围和不纳入项”已勾选。
- 本记录可供新 Issue、PR、API、数据库、权限和测试任务引用。
- 本记录不作为 M1～M5 业务功能已经实现的证据。
