# 项目范围说明

## 目标

建设银行触点载体管理系统 V1.3.2，维护组织、员工、NFC 触点载体、载体内容、绑定关系，并接收 LinkForty 事件形成可查询的访问事件和统计指标。

## 系统边界

### 银行后台负责

- M1：后台访问与操作审计
- M2：组织与员工管理
- M3：NFC 触点资产与载体内容管理
- M4：触点载体员工绑定管理
- M5：访问事件接入与关联管理

统计与报表、批量导入、异步任务以及 Casdoor、LinkForty、NFC 集成属于横向或外部能力，不占用 M 编号。V1.3.2 统计与报表验收点击和访问数据；安装/App 聚合字段保留兼容结构但不提供成功能力，相关数据不拥有本地专属表，后续版本重新评估。

### LinkForty Core 负责

- Link、短码和跳转运行时
- 点击、安装和 App 事件原始事实
- 对外 Webhook 投递
- LinkForty 平台自身 API 和数据维护

银行后台对 LinkForty 的写入必须通过 API；读取事件表时使用受限只读账号，不允许通过数据库直读 `webhooks.secret`，不允许执行 LinkForty DML、DDL 或 TRUNCATE。Secret 只能由受控 Core API provisioning 一次性交付给银行配置服务。

## MVP 范围

- 一期只支持 NFC 触点载体。
- M3 同时维护可复用地址页面主数据；地址页面可按资产权限被载体内容选择，不属于 `target_resources` 或 `routing_rules`。
- 地址页面至少包含责任组织 `org_id`、地址编码/标识、内容类型（小程序、APP、网页）、`url`、`target_url` 和 `status`；`url` 只做首尾空格清理，不做通用 HTTP/HTTPS 审查。
- 同一张 NFC 卡的 LinkForty 短链可以通过地址页面切换目标而不重新写卡：`payload_value` 和 `linkforty_link_id` 保持不变。网页和小程序直接把目标提交给 Core；小程序必须使用公开 HTTPS Universal Link；APP 使用 `card-switch-demo` 的 `app-open.html` Bridge URL。
- Casdoor 作为身份、角色和功能权限权威。
- 银行后台用 Token 的 `employee_code` Claim 定位 `employees`，并按业务表范围字段执行数据过滤。
- `access_events` 不分区，`event_id` 全局唯一，`click_id` 非唯一。
- MVP 不包含银行办理量、办理金额和真实业务转化结果。
- V1.3.2 不包含目标资源和路由发布。M3 通过 LinkForty API 发起外部调用，Worker 执行重试和补偿，M1 通过 `operation_logs` 和 `trace_id` 记录结果；`touchpoint_payloads` 不保存外部同步状态。
- Core 与银行数据库不形成单一事务；目标切换采用 Core 更新优先、银行落库、失败补偿的最终一致方案。应用启动只做数据库连接检查，不自动执行 Alembic 迁移；迁移由部署流程显式执行。

## 明确不纳入本期

- 二维码、条形码等其他介质的完整流程
- 银行业务办理量和金额接口
- 复杂审批流
- 实时路由计算
- 完整版本可视化回滚
- 自动化 NFC 硬件写卡（除非硬件和 SDK 已确认）

## 当前状态

当前工作区中的 `bank-touchpoint-backend/`、`bank-touchpoint-frontend/` 和 `docs/` 分别是银行后台后端、前端和协作资料目录；前后端与数据库目前仅有工程基线和占位模块。`linkforty/core/` 是独立的 LinkForty Core TypeScript 服务，`card-switch-demo/` 仅为演示项目，均不属于银行后台业务实现。

## 里程碑

| 阶段 | 目标 | 完成标准 |
|---|---|---|
| P0 | 边界和外部契约冻结 | Casdoor、LinkForty、Webhook、NFC 的关键事实有负责人和结论 |
| P1 | 工程基础 | 后端、前端、数据库、Redis、迁移和 CI 可运行 |
| P2 | 工作包 A 闭环 | M1～M3 完成审计、主数据和触点资产基础能力 |
| P3 | 工作包 B 闭环 | M4～M5 完成绑定生命周期、访问事件和运营闭环 |
| P4 | 横向能力闭环 | 统计与报表、导出、异步补偿和操作审计完成验收 |
| P5 | 上线准备 | 权限、安全、性能、备份和回滚验收通过 |

## 成功标准

- 关键业务流程可通过前端完成。
- 所有后端接口都有权限和数据范围校验。
- 事件重复提交不会产生重复 `access_events`。
- LinkForty 外部失败可追踪、重试和人工处理。
- 关键命令和导出都有操作审计。
- 数据库迁移、备份和回滚流程可验证。
