# 幂等规范

## V1.3.2 适用对象

- 绑定、解绑、转交和状态命令使用领域业务唯一键或命令键。
- 资产、组织、员工和 Payload 创建使用业务唯一键；重复键返回冲突或首次业务结果，按接口契约执行。
- LinkForty 创建接口沿用现有稳定业务幂等策略；目标切换的 Core `PUT` 不添加 Core 尚未声明支持的幂等请求头，使用同 Link ID + 同目标的逻辑幂等。
- Webhook 使用 `event_id` 全局唯一；`click_id` 只作非唯一逻辑引用。
- `/imports/validate` 只读校验，不写业务表；物理删除命令使用专用 `master_data_delete_commands`，不作为普通业务写入的通用幂等表。
- 地址页面普通创建不再接收客户端 `addressCode`：服务端按内容类型前缀在事务级 advisory lock 下分配全局序号，并以唯一约束作为并发最终防线；可信导入更新仍以已有 `addressCode` 匹配，新增导入行可留空并由服务端生成。

## 规则

- 普通 V1.3.2 接口不新增通用幂等表；员工和地址页面物理删除是受控例外，使用 `master_data_delete_commands` 持久化命令和首次成功响应。
- 物理删除相同 `Idempotency-Key` 且请求摘要一致时回放首次结果，不重复写归档、DELETE 或成功审计；相同键但资源/原因不同返回 `IDEMPOTENCY_KEY_REUSED`。资源已被其他键删除时返回 `RESOURCE_ALREADY_DELETED`。
- 通用 `Idempotency-Key` 持久化、首次响应回放、TTL、Payload 冲突和并发回放延期 V1.4。
- Webhook 使用 `event_id` 全局唯一。
- `click_id` 不得作为唯一键。
- 数据库唯一约束是并发最终防线。
- 领域命令重复提交必须返回幂等成功、状态冲突或唯一键冲突中的一种明确结果；不得重复产生业务事实或审计事实。服务端编号创建的重试由事务锁和唯一约束保证不产生重复编号，但未引入通用响应回放。
- 外部 API 请求按外部契约携带稳定标识；不向不支持的 Core `PUT` 强行添加请求头。
- 地址页面 PATCH 使用对象级版本/幂等策略；enable/disable 为状态命令，同一目标状态重复提交幂等成功。目标配置变化在地址页面本地事务提交后创建带 `page_config_hash` 的重新应用任务；展示字段变化不创建任务。Payload 地址切换使用 `POST /touchpoint-payloads/{id}/switch-address-page`，同一 Link、同一目标和同一地址页面返回 `NO_CHANGE`，不调用 Core。选中的页面目标必须由 Service 从数据库读取。
- 重新应用任务使用稳定的任务 ID 和 `address-page-reapply:{job_id}` Celery task ID；任务明细按 Payload 独立重试，重试前重新校验地址页面版本和组织范围。任务记录是银行后台异步事实，不向 `touchpoint_payloads` 增加外部同步状态。
- 地址页面目标应用按 Payload 加锁；Core 与银行数据库无法单一事务，使用外部状态预校验和补偿更新保证最终一致。银行落库失败也必须补偿 Core；LinkForty Core 当前不保证 `Idempotency-Key` 的严格 exactly-once，创建重试可能产生重复 Link，属于已记录风险。

## V1.4 预留

通用响应回放机制可在 V1.4 通过独立持久化表实现；Redis 只能做加速层，不能成为最终事实来源。

## 禁止

- 只用 Redis 做最终幂等判断。
- 只用内存集合保存幂等键。
- 用到达时间替代事件时间。
