# ADR-006：触点资产单一业务卡ID直接切换

## 状态

Accepted（2026-09-16；发布前仍需通过迁移和并发验收）

## 背景

`touchpoint_assets` 曾同时具有服务端生成的字符串 `asset_id` 和调用方提供的 `asset_code`。两个字段都表达资产业务身份，导致创建、筛选、导入匹配、去重、导出及页面展示存在双重语义。已确认不再保留旧 `asset_code` 的查询、导入匹配、创建或重复校验语义，也不需要分阶段兼容切换。

## 决策

- 直接删除 `bank_admin.touchpoint_assets.asset_code` 及其唯一约束；`touchpoint_assets.asset_id VARCHAR(13)` 是唯一业务卡ID，格式为 `PKYYYYMMDDNNN`。
- 卡ID由 M3 Service 生成，按 `Asia/Shanghai` 业务日每日全局 `001`～`999` 递增；数据库事务级 advisory lock（或等价 DB 锁）和唯一约束保证并发安全。历史卡ID沿用既有 `0007` 迁移结果，不在本迁移中重写。
- `touchpoint_assets.id` 保持数值内部主键。Payload、绑定、访问事件等其他资源的数值 `asset_id` 关联以及资源路径继续使用内部数值 ID，不做全局重命名或字符串化。
- 资产创建请求不接受 `assetId`，也不接受旧 `assetCode`；服务端生成的卡ID只在响应、资产列表/详情、查询、导出和其他资产引用模板中出现。
- 资产导入只新增，不匹配或更新既有资产；模板不包含资产编码或卡ID。非空物理 UID 重复时拒绝新增，不以其作为更新匹配键。
- 载体内容和绑定导入通过 `cardId` 精确查找 `touchpoint_assets.asset_id`，转换到 `touchpoint_assets.id` 后执行原有业务 Service；其他写接口继续传内部数值 `assetId`。
- 不建立旧编码别名、交叉映射表或查询兼容层；不新增通用编码表，不修改 LinkForty 数据库。

## 迁移与兼容影响

- 新增 Alembic `0014_drop_touchpoint_asset_code`，只删除银行库旧资产列及唯一约束，不改写任何既有资产、Payload、绑定、事件或 LinkForty 数据。
- 这是破坏性 API/数据结构切换：旧 `assetCode` 查询参数、创建字段、导入列及消费者必须随发布切换到卡ID契约；不存在双写或旧字段兼容期。
- 新导入卡片默认以库存状态创建；原资产状态命令、授权和数据范围校验不变。批次幂等由现有导入契约处理，不新增通用幂等表。
- downgrade 会重建旧 `asset_code` 列，并以现有卡ID填入确定性回退值。被删除的原始资产编码无法恢复；若必须恢复原值，应从迁移前备份恢复，不可声称 downgrade 能还原原始编码。
- 这是破坏性迁移；执行 upgrade 前必须完成并验证可恢复的数据库备份。若需要恢复已删除的原始 `asset_code`，只能从该迁移前备份恢复。

## 验收

- 验证 migration upgrade 删除列、约束；downgrade 生成唯一非空兼容列；不执行 LinkForty DDL/DML/TRUNCATE。
- 验证资产创建、列表/详情/导出、前缀筛选和导入不再读取/写入 `asset_code`；导入不会更新既有资产。
- 验证 payload/assignment/access-event 和资源路径继续使用内部数值 ID；载体内容及绑定 CSV 的 `cardId` 解析后仍写内部数值关联。
- 验证既有 Card ID 生成格式、上海日期边界、每日上限、数据库并发锁、唯一约束和审计。
