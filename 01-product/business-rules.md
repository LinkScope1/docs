# V1.3.2 业务规则

## 通用规则

- 业务对象只能由其责任模块决定状态。
- 前端展示权限不能替代后端权限校验。
- 所有关键命令必须记录 `operation_logs`。
- 所有批量命令必须返回逐条结果或明确的全量事务结果。
- 所有外部调用必须通过任务日志、`trace_id` 和 M1 的 `operation_logs` 记录超时、失败、重试和最终结果，不在业务表中复制外部运行状态。
- `org_id` 表示数据责任组织，`employee_id` 表示直接责任员工；公共或系统事件可为空。

## M2 组织与员工

- `org_code` 全局唯一，根组织为 `1`。
- 下级编码必须以前级编码为前缀并追加恰好三位数字。
- 普通组织新增不接收客户端输入的 `org_code`；服务端锁定父组织后，按同一父组织的直接子级已占用最大序号生成下一个编码，范围为 `001` 至 `999`。
- 组织编码只增不复用；停用、历史或归档记录中的编码仍视为已占用。组织不通过公开导入能力处理；历史数据迁移如需显式编码，必须使用单独受控迁移脚本。
- 组织层级、祖先和下级范围通过编码前缀查询，不保存 `parent_org_id`。
- 停用组织前必须检查启用下级组织和员工。
- 员工只保存一个直接所属组织。
- Casdoor Token 的 `employee_code` Claim 定位本地启用员工。
- 员工物理删除仅允许已停用且无当前绑定、资产/载体内容责任和正在执行员工关系写入任务的员工；禁止删除当前登录员工，并通过独立 `employee.delete` 权限控制。

## M3 触点载体和内容

- MVP 只支持 NFC。
- `touchpoint_assets.asset_id` 是唯一资产业务标识，由服务端生成，格式为 `PKYYYYMMDDNNN`；按 `Asia/Shanghai` 业务日期每日全局从 `001` 递增至 `999`。内部数值 `id` 保持为关系表和路径参数的主键；非空 `carrier_uid` 不得重复。
- 资产库存时 `employee_id` 可以为空；绑定、解绑、转交必须同步资产和内容的责任范围。
- 资产不再保存 `config_status`、投放 `location_code` 或 `door_no`。
- Payload 的 `payload_value` 保存卡内实际内容；若关联地址页面，`address_page_id` 和 `target_url`
  仅用于记录所选主数据及其当时解析出的实际内容，不构成 `target_resources` 或 `routing_rules`。
- M3 维护可复用地址页面 `touchpoint_address_pages`；页面按 `org_id` 归属组织，可供同组织及下级资产选择。
- 地址页面 `content_type` 为 `1=小程序`、`2=APP`、`3=网页`；同时保存 `address_name`、`status`、`url` 和 `target_url`。
- 地址页面的 `url` 只校验非空和长度；`target_url` 按内容类型校验：小程序必须是公开 HTTPS Universal Link，APP 的回退地址允许 HTTP/HTTPS，Bridge 必须是公开 HTTPS，网页直接使用目标地址。Payload 选择页面时由后端读取数据库 `target_url`，不能信任前端传值。
- 只有启用地址页面出现在资产下拉选项中；页面停用不解绑历史 Payload、不改写 NFC；目标配置修改先提交地址页面主数据和审计，再由异步任务复用统一应用流程重新应用到历史绑定 Payload，保持 `payload_value` 不变。
- 已停用地址页面可通过独立 `touchpoint.address-page.delete` 高风险权限物理删除；删除前锁定页面并阻止 queued/running 重新应用任务，归档快照、删除命令和审计与主表 DELETE 在同一事务中完成。既有 Payload、NFC、LinkForty 状态和历史任务不修改，历史查询通过归档快照解析。
- 地址页面 `content_type=1` 的小程序目标必须是公开 HTTPS Universal Link；`content_type=2` 的 App 配置保存在 `metadata.app`，由银行后台按公开 `app-open.html` Bridge 协议生成目标；`content_type=3` 的网页直接使用 `target_url`。
- LinkForty Link 仅当 `asset_status=1`、`touchpoint_payloads.status=1`、`provider_type=1` 且 `linkforty_link_id` 非空时允许 active；任一条件不满足都必须 inactive。首次绑定创建 Link 后按该谓词同步，资产或 Payload 状态变更通过 LinkForty API 同步，不在 Payload 中增加外部同步状态字段。
- `linkforty_link_id` 仅为 LinkForty 逻辑引用；Payload 不保存 LinkForty 专属同步状态、同步时间、错误摘要或重试次数。

## M4 绑定

- 同一载体同一有效时间范围内只能有一个有效员工绑定。
- 有效期不能重叠。
- 绑定记录只追加，不覆盖历史。
- 不保存组织名称、支行名称或员工名称快照；历史查询使用当前主数据名称。

## M5 访问事件

- 缺少 `event_id` 的 Webhook 拒绝处理。
- `event_id` 是全局唯一幂等键。
- `click_id` 不是唯一键。
- 重复 `event_id` 返回幂等成功。
- 事件关联结果写入事件发生时识别到的 `org_id` 和 `employee_id`。

## 批量导入

- 公开主数据导入支持卡片、载体内容、员工和可复用地址页面四类模板；组织导入不属于公开能力。
- 员工绑定、解绑和转交使用独立生命周期模板或资产批量命令，不混入主数据导入。
- 资产导入只创建新资产，不匹配或更新既有资产；模板不包含资产编码或卡ID，卡ID由服务端自动生成。
- 载体内容和员工绑定导入使用 `cardId` 精确解析已有资产，再使用内部数值 `id` 建立关系；组织和员工仍分别使用 `org_code`、`employee_code`。
- 非空 `carrier_uid` 重复时拒绝新增，不把 UID 用作资产导入的更新匹配键。
- 文档缺少某行不代表删除、停用或解绑。
- 解绑或转交必须使用显式 `operation` 类型；不支持通过缺失行推导任何状态变化。
- 导入必须支持预校验、幂等键、逐行结果和审计。

## 本版本不纳入能力

目标资源、路由规则、路由发布和路由冲突不属于 V1.3.2；本版本不定义相关表、API、状态或发布能力。

## 统计与报表横向能力（不编号）

- 统计与报表不拥有本地专属表；V1.3.2 成功统计只读取 M5 的 `access_events` 和已支持的 LinkForty 点击数据。
- 点击使用 `click_events.clicked_at`。
- 访问使用 `access_events.received_at`。
- 安装统计使用 `install_events.installed_at` 的目标口径，但安装聚合成功能力不纳入 V1.3.2。
- App 事件统计使用 `in_app_events.event_timestamp` 的目标口径，但 App 聚合成功能力不纳入 V1.3.2。
- 点击统计默认排除机器人。
- 安装/App 聚合字段在银行侧保留兼容结构；必要能力未支持时整体返回 `503 DATA_SOURCE_UNAVAILABLE`，不返回伪造零值或部分成功。
- 银行业务办理量不纳入 MVP 正式验收。
