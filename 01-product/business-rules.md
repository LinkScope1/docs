# 业务规则

## 通用规则

- 业务对象只能由其责任模块决定状态。
- 前端展示权限不能替代后端权限校验。
- 所有关键命令必须记录 `operation_logs`。
- 所有批量命令必须返回逐条结果或明确的全量事务结果。
- 所有外部调用必须记录超时、失败、重试和最终状态。

## M2 组织与客户经理

- `org_code` 全局唯一。
- 组织树不能形成环。
- 停用组织前必须检查启用子组织和客户经理。
- 客户经理只保存直接所属组织。
- 客户经理停用不直接修改触点资产状态。

## M3 触点载体

- MVP 只支持 NFC。
- `asset_code` 唯一。
- 非空 `carrier_uid` 不得重复。
- `asset_status` 与 `config_status` 独立维护。
- Payload 保存卡内实际内容，不保存最终跳转目标。

## M4 绑定

- 同一触点在同一有效时间范围内只能有一个有效绑定。
- 有效期不能重叠。
- 转交必须追加历史记录并保存组织、支行和客户经理快照。
- 历史快照不能随主数据变化而漂移。

## M5/M6 资源和路由

- `link_id` 与 `resource_value` 严格二选一。
- 路由作用域必须与对象类型匹配。
- 匹配优先级为 `CARRIER > MANAGER > BRANCH > GLOBAL`。
- 路由发布必须经过确认。
- M3 `external_sync_status` 不得替代 M6 `publish_status`。

## M7 事件

- 缺少 `event_id` 的 Webhook 拒绝处理。
- `event_id` 是全局唯一幂等键。
- `click_id` 不是唯一键。
- 重复 `event_id` 返回幂等成功。
- 绑定、路由和目标快照按事件发生时间读取。

## M8 统计

- 点击使用 `click_events.clicked_at`。
- 访问使用 `access_events.received_at`。
- 安装使用 `install_events.installed_at`。
- App 事件使用 `in_app_events.event_timestamp`。
- 点击统计默认排除机器人。
- 银行业务办理量不纳入 MVP 正式验收。
