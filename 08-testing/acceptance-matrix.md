# V1.3.2 验收矩阵

| 需求编号 | 模块 | API/对象 | 测试用例 | 状态 |
|---|---|---|---|---|
| M1-AUTH-001 | M1/BFF 登录 | `/auth/login`、`/auth/callback` | state、nonce、S256 PKCE、服务端 Token Exchange、`AUTH_FRONTEND_BASE_URL` 加固定回调路径；不连接真实 Casdoor | 条件开发：Fake 覆盖 |
| M1-AUTH-002 | M1/Session | Redis state/Session | state 缺失、过期、重复使用、不匹配立即删除；Session TTL、过期、删除和 logout | 条件开发：Fake 覆盖 |
| M1-AUTH-003 | M1/JWT | OIDC Client/JWKS | 签名、issuer、audience、subject、nonce、exp、60 秒偏差、unknown kid 刷新 | 条件开发：测试签名覆盖，平台契约待确认 |
| M1-AUTH-004 | M1/安全 | Cookie/Origin | HttpOnly、Path、SameSite、生产 Secure、允许 Origin 和 `AUTH_ORIGIN_NOT_ALLOWED` | 条件开发 |
| M1-001 | Casdoor 登录 | `/auth/me` | JWT、Claim 缺失、停用员工、越权 | 条件开发：真实 Casdoor 外部契约待确认 |
| M2-001 | 组织维护 | `organization_units` | 编码唯一、前缀分段、停用阻断 | 待测 |
| M2-002 | 员工维护 | `employees` | 员工编码唯一、组织范围、状态 | 待测 |
| M3-001 | 触点资产 | `touchpoint_assets` | 资产编码、UID 唯一、状态、范围字段 | 待测 |
| M3-002 | 载体内容 | `touchpoint_payloads` | 内容类型、实际写入值、范围同步、LinkForty 逻辑引用、无本地同步状态字段；地址切换保持 `payload_value`/Link ID 并更新 Core 目标快照 | 待测 |
| M3-003 | 可复用地址页面 | `touchpoint_address_pages`、`/touchpoint-address-pages` | 组织范围、地址编码唯一、内容类型（小程序/APP/网页）、`url` 原始值兼容、Core 目标传播、失败补偿、启停保留历史、Payload 下拉选项 | 待测 |
| M4-001 | 绑定 | `touchpoint_employee_assignments` | 重叠、当前唯一、历史无快照、转交 | 待测 |
| M5-001 | Webhook | `access_events` | 签名、幂等、重复 click、关联重试 | 通过：本地真实联调和负责人正式确认已完成 |
| INT-LINKFORTY-NGINX-001 | LinkForty 外部集成 | Nginx `/linkapi/`、Webhook location | `/linkapi/` 路径映射、Core health/API/短链、HTTP/1.1、Header、缓存、方法/Body/`Idempotency-Key` 保留；Webhook 原始 body 和签名 Header 保留 | 待执行：测试拓扑 |
| CAP-ANL-001 | 统计与报表横向能力（不编号） | analytics | 点击/访问时间、机器人、范围、只读边界、审计；安装/App 不支持时整体 503 | 通过 |
| IMP-001 | 文档导入预留 | `/imports/validate` | 模板、稳定匹配键、逐行错误 | 待测 |
| IMP-002 | 文档导入预留 | `/imports/execute` | 更新并新增、幂等、显式解绑、审计 | 待测 |
| IMP-003 | 地址页面导入导出 | `address_page`、`touchpoint-address-pages` | 中文固定表头、预校验、逐行失败、重复导入、缺失行不停用、权限范围和字段白名单 | 待测 |

## 认证外部证据门禁

- 本矩阵的认证“条件开发”只表示代码边界、Fake/Mock 和负向测试具备，不表示真实 Casdoor 已连接。
- 真实 issuer、audience、JWKS URI、Claim、角色/权限编码和员工停用同步仍对应延期的 `P0-CAS-001～006`、`DEC-CAS-001～006`，不得因本地测试通过而改为完成。
- 默认单元测试不得执行 Casdoor 网络调用，不得使用真实 Secret；前端 E2E 只 Mock `/api/v1/auth/me` 和认证状态。

### CAP-ANL-001 验收证据（2026-09-07）

- 测试文件：`bank-touchpoint-backend/tests/test_analytics_service.py`、`test_analytics_api.py`、`test_analytics_database_integration.py`、`test_integrations.py`、`test_openapi_contract.py`。
- 测试命令：后端统计定向测试（Docker PostgreSQL 测试端口 `15432`，连接密码不记录）；结果 `65 passed`。Ruff、mypy 和后端全量测试分别为通过、95 个源文件无错误、`898 passed, 56 skipped`。
- 时间口径：`from` 包含、`to` 排除；访问统计读取 `access_events.received_at`；重复 `click_id` 按事件行计数；带时区 RFC3339 参数和非法请求前置校验均已覆盖。
- 机器人排除边界：点击数只接受 LinkForty Core 的 `totalClicks`；银行后台不读取 `is_bot`、`clicksByDate`、点击事件表或 LinkForty 数据库；当前 Core 只能表达滚动 `days` 时，精确 `[from,to)` 查询 fail-closed。
- 数据范围：GLOBAL、ORG_SUBTREE、ORG_SELF、EMPLOYEE_SELF、ASSET_SCOPE 和 `orgCodePrefix` 收窄同时作用于访问统计和 Link 选择；越权返回 403 `DATA_SCOPE_DENIED` 且不访问数据源。
- API-only/只读边界：统计唯一入口为 `/api/v1/analytics/summary`；不使用 `bank_linkforty_ro`，不读取 `install_events`/`in_app_events`，不新增本地统计表或 Alembic migration，不执行外部 DML/DDL/TRUNCATE；数据库测试使用事务回滚并比较表/列/索引签名。
- 不支持能力：点击精确窗口、安装聚合、App 事件聚合、LinkForty API 未配置、数据源失败或非法计数均返回整体 `503 DATA_SOURCE_UNAVAILABLE`，无 `data`、零值、部分成功结果或内部连接/表名/堆栈详情。

## M5-001 当前进度

- Core `1.21.0` 真实访问短链后投递 `click_event`，银行接收端返回 202 并完成 HMAC-SHA256 验签。
- 已确认字段路径：`event`、`event_id`、`timestamp`、`data.id`、`data.linkId`；真实 body SHA-256 为 `29b71f9eb0a8989b9af32533ea944cd489ec856a34c6d4b29c3cb38c564dfc43`。
- 同一完整请求重复投递只保留一条 `access_events`；body 篡改和签名篡改返回 401；删除 `event_id` 返回 400。
- 一次性失败探针已观察到 500 → 202，间隔约 1.027 秒；探针和旧测试数据已清理。
- 证据目录：`/private/tmp/linkforty-webhook-evidence/`（仓库外、限权、不纳入 Git）。
- 正式关闭条件已满足：LinkForty 负责人已确认签名、字段和重试契约。
