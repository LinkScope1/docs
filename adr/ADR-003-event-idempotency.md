# ADR-003：使用 event_id 作为访问事件全局幂等键

## 状态

Accepted

## 决策

`access_events.event_id` 建立全局唯一约束，`click_id` 只作为非唯一逻辑引用和普通索引。

## 原因

- 同一个点击可能产生多个不同业务事件。
- Webhook 可能重复投递。
- 数据库唯一约束是并发场景的最终防线。

## 验收

- 重复 `event_id` 幂等成功。
- 相同 `click_id` 的不同 `event_id` 可以保存。
- 并发提交不会产生重复访问事件。
