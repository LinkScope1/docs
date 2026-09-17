# ADR-005：触点资产卡ID与内部主键兼容

## 状态

Superseded by [ADR-006](./ADR-006-touchpoint-asset-single-business-id.md)

## 背景

现有 `touchpoint_assets.id` 是跨表使用的数值内部主键，`asset_code` 是既有业务编码和导入稳定键。页面需要一个可供业务人员识别的卡ID，但不能改变 Payload、绑定关系、访问事件或现有路径参数的数值关联语义。

## 决策

- 在 `bank_admin.touchpoint_assets` 增加服务端生成的 `asset_id VARCHAR(13)`，格式固定为 `PKYYYYMMDDNNN`。
- 业务日期使用 `Asia/Shanghai`；三位编号按日期全局递增 `001`～`999`。Service 编排生成，Repository 在同一事务中使用 PostgreSQL transaction-level advisory lock 查询序号，数据库唯一约束作为最终防线。
- 历史数据按 `created_at` 转换后的业务日期、`created_at ASC, id ASC` 回填；单日超过 999 条时迁移失败并回滚。
- `id`、`asset_code` 和既有跨表数值 `asset_id` 关联保持不变。创建请求和导入请求不得提交或覆盖卡ID，卡ID只在响应、列表、详情和标准资产导出中返回。

## 影响

- 新增 Alembic `0007_touchpoint_asset_id`、格式检查、非空约束和全局唯一约束；不新增通用编码表，也不修改 LinkForty 表。
- 资产页面新增卡ID列、前缀查询和详情展示；创建成功提示返回服务端生成值。
- 卡ID创建冲突返回稳定的 409；达到每日上限返回 `ASSET_ID_EXHAUSTED`，事务回滚不要求编号无间隙。

## 验收和风险

- 本地专项单元/路由/导出测试和迁移静态契约测试已执行；真实 PostgreSQL migration upgrade/downgrade、历史回填和多会话并发测试需在数据库环境执行。
- 回滚方式为停止使用新字段后执行经审批的 `alembic downgrade 0006_touchpoint_address_pages`；执行前必须完成备份并确认调用方已回退到不依赖 `assetId` 的版本。

> 本决策记录的是 `asset_id` 与 `asset_code` 并存的历史方案；2026-09-16 起由 ADR-006 取代。
