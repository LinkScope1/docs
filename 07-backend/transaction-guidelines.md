# Service / Repository 数据库事务规范

## 1. 适用范围

本规范适用于 M1–M5 的 FastAPI请求、批量导入、Worker任务和补偿命令。银行后台使用 SQLAlchemy 2.x异步Session；Casdoor、LinkForty和NFC外部调用由 Integration处理。

## 2. 分层职责

~~~text
Router → Service → Repository → ORM → PostgreSQL
                 ↘ Integration / Worker
~~~

### Router

- 解析HTTP参数、认证依赖、幂等键和响应模型。
- 调用Service，不直接使用SQLAlchemy、执行SQL或调用Repository。
- 不决定状态转换、逻辑外键、数据范围和事务提交。

### Service

- 负责权限与数据范围、逻辑外键、状态转换和业务幂等校验。
- 拥有业务事务边界，编排多个Repository、审计和任务。
- 一个Service命令要么完整成功，要么回滚全部本地业务变化。
- 不把数据库Session、ORM对象或数据库异常暴露给Router。

### Repository

- 负责SQLAlchemy查询、持久化、必要的 flush、行锁和分页查询。
- 不执行 commit 或 rollback；事务由Service控制。
- 不决定功能权限、状态是否合法、是否调用外部系统或最终错误文案。
- 不返回跨请求存活的Session绑定对象；响应前由Service映射为Schema。
- 不建立万能Repository；各模块按查询语义定义明确方法。

### Integration

- 负责Casdoor、LinkForty和NFC调用、超时、协议错误映射和最小字段转换。
- 不接收Repository职责，不直接写银行业务表。
- 外部系统写入坚持API-only，不直接执行LinkForty DML或迁移。

### Worker

- 每个任务或每次重试创建独立Session和事务，禁止复用Web请求Session。
- 通过Service执行状态变化，不绕过业务规则直接写Repository。
- 重试次数、退避和最终失败必须通过任务日志、trace_id和M1 operation_logs追踪。

## 3. Session生命周期

- Web请求通过FastAPI依赖获取一个异步Session，请求结束必须关闭。
- Worker任务在任务入口创建Session，在任务结束或异常后关闭。
- Session不得保存在全局变量、单例、缓存、AccessContext或跨任务对象中。
- 只读查询不调用 commit；写命令由Service开启明确事务。
- 不允许在同一Session中并发执行多个协程。

推荐写命令结构：

~~~python
async def execute_command(session: AsyncSession, ...) -> Result:
    async with session.begin():
        # 权限、引用和状态校验
        # Repository写入和flush
        # 成功操作审计
        ...
    return result
~~~

- session.begin 正常退出时提交，异常退出时回滚。
- 被上层事务调用的Service不得再次开启独立顶层事务；内部方法接收同一Session。
- Repository仅在需要立即取得约束结果、生成值或后续查询依赖写入结果时调用 flush。

### LinkForty 目标应用的两阶段边界

- 地址页面 PATCH 的第一笔短事务只保存 `touchpoint_address_pages` 和成功审计；目标配置
  变化后，提交完成再创建重新应用任务和投递 Worker。任务明细按当前页面与调用方组织范围
  重新查询，不接受客户端资产列表。
- Payload 目标应用先在短事务中锁定并快照 Payload、资产和地址页面，事务外执行 LinkForty
  GET/PUT，再以第二笔短事务重新校验页面 hash、Payload 关系、外部 Link ID 和权限后落本地
  `address_page_id`/`target_url`。禁止在本地锁和事务内执行外部 HTTP。
- 外部成功而第二笔本地事务失败时恢复旧目标；新建 Link 后本地创建失败时通过 API 删除新
  Link。补偿失败只记录 `LINKFORTY_COMPENSATION_FAILED`，不伪造本地成功。

## 4. 本地原子事务

以下操作必须在单一数据库事务中完成：

- 新增或修改业务对象及其成功操作日志。
- M4绑定：新增绑定记录、更新资产责任范围、同步全部载体内容责任范围、写操作日志。
- M4解绑：结束当前绑定、清空资产和内容当前员工、写操作日志。
- M4转交：结束旧绑定、新增新绑定、同步资产和内容组织/员工、写操作日志。
- M5事件落库：写入幂等事件、关联资产/绑定/组织/员工及成功审计。
- 需要全量原子性的批量命令：任一行失败则整批回滚。

规则冲突时不得先提交部分业务状态再返回错误。

## 5. 成功和失败审计

- 成功审计与业务变化使用同一事务；业务回滚时成功日志必须一起回滚。
- 业务校验、数据库约束或外部调用失败后，先结束并回滚业务事务，再使用独立短事务写失败日志。
- 失败日志写入失败不得覆盖原始业务异常；必须记录脱敏应用日志并触发监控。
- operation_logs只追加，不更新或删除。
- 审计数据只保存必要前后字段、错误码和摘要，不保存Secret、Token、完整敏感请求或SQL。

## 6. 并发和数据库约束

- 业务预检查用于提供可读错误，数据库唯一约束、排他约束和事务锁是并发最终防线。
- 唯一编码、NFC UID、event_id和当前绑定冲突必须捕获数据库 IntegrityError 并映射为稳定的409错误码。
- M4绑定、解绑和转交在读取当前资产与绑定时使用明确的 SELECT FOR UPDATE 行锁顺序：先锁资产，再锁当前绑定。
- 所有涉及多张资产和员工的批量操作必须按稳定ID顺序加锁，降低死锁风险。
- 死锁、序列化失败只允许在明确幂等的命令或Worker任务中有限重试，不得无限重试。
- Redis和内存锁不能替代PostgreSQL唯一约束或事务锁。

## 7. 外部调用与本地事务

- 禁止在数据库事务中等待长时间HTTP、NFC设备或文件上传操作。
- 调用外部系统前先在短事务或只读查询中完成权限、数据范围和输入校验，然后结束数据库事务。
- 外部调用必须携带稳定幂等键和 trace_id。
- 外部调用完成后开启新的短事务，保存必要逻辑引用、业务结果和成功审计。
- 外部成功但本地提交失败时，不假设外部操作失败；通过同一幂等键查询或重放，并由Worker执行补偿和对账。
- 本模型没有通用Outbox或外部同步状态表，不得临时向业务表增加同步字段；需要持久化任务状态时必须先变更物理模型。

## 8. 批量导入和部分成功

- 每个批量API必须在契约中选择“全量事务”或“逐条结果”，不得隐式混用。
- 全量事务：预校验全部通过后在一个事务写入；任一数据库错误整批回滚。
- 逐条结果：每行或每个明确分组使用独立事务，返回逐条成功和失败结果；不得因部分成功返回虚假的整体成功。
- 重复导入使用 Idempotency-Key 和稳定业务键，数据库唯一约束作为最终防线。
- 大批量导入由Worker执行，避免Web请求持有长事务。

## 9. 异常映射

| 异常场景 | 事务行为 | API错误 |
| --- | --- | --- |
| 请求结构错误 | 不开启写事务 | 422 REQUEST_SCHEMA_INVALID |
| 业务规则或逻辑外键失败 | 回滚 | 400 VALIDATION_ERROR或对应业务错误 |
| 对象不存在 | 回滚 | 404 RESOURCE_NOT_FOUND |
| 权限或数据范围不足 | 不写业务数据 | 403 PERMISSION_DENIED或DATA_SCOPE_DENIED |
| 唯一、状态或绑定冲突 | 回滚 | 409 DUPLICATE_CODE、STATE_CONFLICT或ASSIGNMENT_CONFLICT |
| 外部API失败 | 不保持数据库长事务 | 502 EXTERNAL_API_ERROR、503 DATA_SOURCE_UNAVAILABLE或504 EXTERNAL_API_TIMEOUT |
| 未预期异常 | 回滚并记录脱敏日志 | 500 INTERNAL_ERROR |

Repository不得把SQL、表名、驱动错误或连接信息直接返回给调用方。

## 10. Repository方法约定

- 方法名表达查询意图，例如 get_by_id、get_by_employee_code、list_in_scope、lock_current_assignment。
- 返回 None 表示未找到，由Service映射为业务错误；Repository不构造HTTP异常。
- 分页查询必须应用访问范围和筛选条件后再计算 total。
- 排序字段使用Repository白名单，禁止直接拼接客户端 sortBy。
- 默认不加载不需要的关系和大JSON字段，避免N+1查询和无边界结果集。

## 11. 测试要求

公共事务基础和各模块写命令至少覆盖：

- 成功提交。
- 中间步骤异常时完整回滚。
- 成功审计与业务数据原子提交。
- 失败审计在回滚后独立写入。
- 逻辑外键不存在、停用和跨组织校验。
- 唯一约束、当前绑定和时间重叠并发冲突。
- 外部调用超时不长期占用数据库事务。
- Worker重试不会产生重复业务记录。
