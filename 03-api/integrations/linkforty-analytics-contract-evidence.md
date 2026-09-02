# X-ANL-004：LinkForty 安装/App API 契约核验报告

## 结论

| 项目 | 结果 |
| --- | --- |
| 核验日期 | 2026-09-02 |
| 当前状态 | **阻塞待确认** |
| 是否关闭 X-ANL-004 | **否** |
| 核验范围 | LinkForty Core 安装事件和 App 事件的正式聚合读取 API、时间口径、范围映射、API-only 边界和失败语义 |

当前没有足够证据关闭 X-ANL-004。Core 当前可观察到安装/App 数据模型和 SDK 写入接口，但没有发现正式的安装聚合或 App 事件聚合读取接口，也没有发现可验证的精确 `[from,to)` 契约、银行组织/员工范围映射、生产网络安全证明或 LinkForty 负责人确认。

因此，银行后台继续使用 API-only、fail-closed 方案：非空 LinkForty 范围下，安装/App 聚合能力未提供或未确认时返回 `503 DATA_SOURCE_UNAVAILABLE`，不查询 Core 数据库、不使用 `bank_linkforty_ro`、不伪造 `0`，也不返回部分成功。

## 1. 证据索引

### 1.1 代码和文档证据

| 证据 | 可观察事实 | 判定 |
| --- | --- | --- |
| LinkForty Core `src/routes/analytics.ts` | 仅注册 `GET /api/analytics/overview` 和 `GET /api/analytics/links/:linkId`；参数是可选 `userId` 和滚动 `days`，查询使用 `NOW() - INTERVAL`。 | 只有点击聚合；不能表达 X-ANL-004 所需的安装/App 精确区间。 |
| LinkForty Core `src/routes/sdk.ts` | 注册 `POST /api/sdk/v1/install` 和 `POST /api/sdk/v1/event`。前者写入安装事件并返回安装/归因结果，后者写入 App 事件并返回 `eventId`/`acknowledged`。 | 这是事件接入/写入，不是聚合读取 API。 |
| LinkForty Core `src/lib/database.ts` | 存在 `install_events.installed_at`、`in_app_events.event_timestamp` 等数据库字段。 | 只能证明 Core 内部模型字段存在，不能证明外部 API 契约。 |
| Core `README.md`、`SDK_SPEC.md` | Analytics 文档仅说明 overview、单 Link 点击分析和 SDK 写入接口；未发现安装/App 聚合读取端点。 | 未发现正式安装/App 聚合契约。 |
| 银行后台 `src/app/integrations/linkforty/read_only.py` | `count_installs()` 和 `count_in_app_events()` 对非空 Link 范围明确抛出能力不可用；精确区间点击统计同样拒绝使用滚动窗口近似。 | API-only fail-closed 已落地。 |
| 银行后台 `src/app/modules/analytics/service.py` | 统一调用外部三项统计；任何外部异常统一转换为 `503 DATA_SOURCE_UNAVAILABLE`，不返回部分结果。 | 四计数器失败闭环已固化。 |
| 银行后台配置和数据库会话 | 仅配置银行侧 `DATABASE_URL` 和 `LINKFORTY_BASE_URL`；未发现 LinkForty 数据库连接。 | 未建立跨库直连。 |

### 1.2 版本和工作区基线

| 仓库 | 核验版本 | 工作区变化处理 |
| --- | --- | --- |
| `bank-touchpoint-backend` | `2b150db` | 保留用户已有 `tests/test_analytics_database_integration.py` 修改。 |
| `docs` | `d05403d` | 保留用户已有 `00-project/development-task-checklist.md` 修改；X-ANL-004 未改为完成。 |
| `linkforty/core` | `3c3a877`，包版本 `1.21.0` | 保留用户已有 `docker-compose.yml` 修改；本任务不修改 Core。 |

## 2. 当前可观察接口矩阵

| 能力 | 当前方法和路径 | 当前可见请求/响应 | 与 X-ANL-004 的关系 |
| --- | --- | --- | --- |
| 点击分析 | `GET /api/analytics/overview?userId=&days=`；`GET /api/analytics/links/:linkId?userId=&days=` | 返回 `totalClicks`、`uniqueClicks`、趋势和维度字段；时间窗口由服务端按滚动天数计算，并排除 `is_bot = false` 之外的记录。 | 由 X-ANL-002 跟踪；不能替代安装/App 聚合，也不能证明精确 `[from,to)`。 |
| 安装接入 | `POST /api/sdk/v1/install` | 请求包括 `userAgent` 以及可选设备、平台、SDK、归因窗口和 `appToken` 字段；响应包括 `installId`、归因结果、置信度和 Deep Link 数据。 | 写入/归因接口，不是安装计数读取接口；不能作为 `installCount` 数据源。 |
| App 事件接入 | `POST /api/sdk/v1/event` | 请求包括 `installId`、`eventName`、可选 `eventData`、`timestamp`、归因和 SDK 字段；响应包括 `eventId`、`acknowledged`。 | 写入接口，不是 App 事件计数读取接口；不能作为 `inAppCount` 数据源。 |
| 安装聚合读取 | 未发现 | 没有可核验的正式方法、路径、参数、响应或错误契约。 | **阻塞**。 |
| App 聚合读取 | 未发现 | 没有可核验的正式方法、路径、参数、响应或错误契约。 | **阻塞**。 |

安全探测只对 SDK 路径发送了 GET 请求，返回 `404 Route GET ... not found`；由于正式路由是 POST，未发送 POST，避免创建真实安装或 App 事件。该探测不能单独证明聚合能力不存在，聚合缺口以 Core 路由、README 和 SDK 规格扫描为依据。

## 3. 正式契约完整性核验

以下表格区分“代码中可见的实现事实”和“可用于银行集成的正式契约”。安装和 App 聚合两列均必须由 LinkForty 负责人提供正式证据后才能变为“已确认”。

| 契约维度 | 安装聚合 | App 事件聚合 | 当前判定/待补证据 |
| --- | --- | --- | --- |
| HTTP 方法和路径 | 未提供 | 未提供 | 需要版本化正式 API 文档或负责人签字确认。 |
| 认证、授权和请求头 | 未确认 | 未确认 | 需要说明认证方式、凭据来源、权限、必需 Header、Trace Header 和凭据轮换。 |
| 请求参数 | 未提供 | 未提供 | 需要 Link 范围、时间参数、组织/员工范围、时区和精度的完整定义。 |
| 响应字段和类型 | 未提供 | 未提供 | 需要明确计数器字段、整数范围、`null`/缺失字段和未知字段处理。 |
| 计数语义 | 未确认是安装事件行数还是去重安装数 | 未确认是事件行数、事件名过滤还是其他口径 | 不能从数据库表名或 SDK 写入响应推导。 |
| 时间字段 | Core 内部字段为 `installed_at` | Core 内部字段为 `event_timestamp` | 需要确认外部字段映射、时区、精度和服务端/客户端时间来源。 |
| 时间范围 | 未确认 `[from,to)` | 未确认 `[from,to)` | 必须提供开始边界包含、结束边界排除的可重复证据。 |
| 组织/员工/触点范围 | 未提供银行 `orgCodePrefix`、员工或资产范围映射 | 未提供银行 `orgCodePrefix`、员工或资产范围映射 | 需要确认银行侧 Link ID 集合如何成为外部过滤条件，并证明不能扩大范围。 |
| 空结果 | 未确认 | 未确认 | 需要区分合法空范围、合法零结果和数据源不可用。 |
| 分页、上限和限流 | 未确认 | 未确认 | 需要单次 Link 上限、响应大小、分页规则、429 语义和 Retry-After 处理。 |
| 错误码和错误体 | 仅观察到 SDK 写入错误，不是聚合契约 | 仅观察到 SDK 写入错误，不是聚合契约 | 需要 4xx、404、409、429、5xx、字段错误和业务失败的正式映射。 |
| 超时、重试和补偿 | 外部正式规则未确认 | 外部正式规则未确认 | 银行客户端已有有界重试，但不能替代平台契约；需确认幂等/重试安全性。 |
| Trace、外部请求 ID 和日志脱敏 | 银行侧记录受控元数据；Core 聚合响应/日志契约未确认 | 银行侧记录受控元数据；Core 聚合响应/日志契约未确认 | 需要确认关联字段和禁止记录内容，不得记录 Token、Secret 或完整敏感响应。 |
| 缓存和一致性 | 未确认 | 未确认 | 需要刷新/延迟/缓存失效规则，否则无法定义统计时效。 |
| 版本兼容和弃用 | Core 包版本为 `1.21.0`；无聚合 API 版本契约 | Core 包版本为 `1.21.0`；无聚合 API 版本契约 | 需要正式版本、兼容窗口和弃用通知规则。 |
| 网络和安全 | 本地 Compose 仅证明 loopback HTTP 可达 | 本地 Compose 仅证明 loopback HTTP 可达 | 生产私网、ACL、防火墙、HTTPS/TLS、证书校验及安全审批仍无证据。 |
| 负责人确认 | 未取得 | 未取得 | 必须有 LinkForty 负责人、银行后端负责人和安全/运维确认记录。 |

## 4. 银行后台当前保护行为

银行后台保持现有 `GET /api/v1/analytics/summary` 契约：

- `from`、`to` 使用带时区时间，并按半开区间 `[from,to)` 校验。
- `accessCount` 只读取银行本地 `access_events.received_at`。
- LinkForty Link ID 先按组织、员工、资产和 `orgCodePrefix` 收窄，`orgCodePrefix` 不得扩大调用范围。
- 非空外部范围下，点击 API 不能表达精确时间区间、安装聚合缺失或 App 聚合缺失，均走能力不可用路径。
- 任一外部指标失败时返回 `503 DATA_SOURCE_UNAVAILABLE`，不返回四计数器部分结果，也不把未知能力伪装成零值。
- 没有本地统计表、LinkForty 数据库连接、`bank_linkforty_ro` 运行时使用或 Core 表的 DML/DDL/查询路径。

空的已授权 Link 范围返回零计数属于“本地范围内没有可调用 Link”的确定结果；它不代表上游安装/App 能力未知时可以伪造零值。

## 5. 验证记录

### 5.1 银行后台

已执行：

```text
pytest -q tests/test_integrations.py tests/test_linkforty_client.py \
  tests/test_api_scaffold.py tests/test_analytics_service.py \
  tests/test_analytics_api.py tests/test_openapi_contract.py
```

结果：`75 passed, 1 warning in 1.56s`。测试覆盖安装/App 能力缺失、精确区间不能由滚动点击 API 表达、无 HTTP 请求、503 无部分成功、范围校验、运行时禁止外部数据库/事件表引用和日志脱敏。

同一变更集的静态验证结果：Ruff `All checks passed`；analytics/LinkForty 相关 mypy `Success: no issues found in 11 source files`；OpenAPI 校验 `41 operations, 38 module mirrors` 通过。

### 5.2 LinkForty Core

此前已执行 Core 全量测试：`13 files, 188 passed, 0 failed`。本任务不修改 Core，因此不以 Core 测试通过替代安装/App 聚合契约证据。

### 5.3 本地运行时只读探测

此前已观察到：

- Core、PostgreSQL、Redis 容器均 healthy；Core 健康和 ready 端点返回 200。
- 点击聚合端点返回 200，并返回点击字段。
- 未发送 SDK 安装或 App 事件 POST 请求，未创建真实业务数据。
- 未建立 LinkForty 数据库连接，未执行 `bank_linkforty_ro` 权限脚本或跨库 SQL。

## 6. 解除阻塞和关闭门槛

LinkForty 负责人需要提供以下完整材料，缺一不可：

1. 安装聚合 API 的正式方法、路径、版本、请求、响应和错误契约。
2. App 事件聚合 API 的正式方法、路径、版本、请求、响应和错误契约。
3. `installed_at`、`event_timestamp` 与外部时间字段的对应关系，以及严格 `[from,to)`、时区和精度证据。
4. 组织、员工、资产和 Link 范围映射，证明银行请求只能收窄数据范围。
5. 空结果、分页、单次上限、限流、超时、重试、缓存和一致性规则。
6. 认证、网络隔离、TLS/证书、ACL、防火墙和安全审批证据。
7. 脱敏的真实只读 API 响应或正式联调记录，包含精确边界样例。
8. 银行后台 API-only、无数据库直连、无伪造零值、无部分成功的测试和静态检查结果。
9. LinkForty 负责人、银行后端负责人和安全/运维负责人的确认记录。

材料齐全后，才允许在银行后台 Client/ReadOnly Adapter 中接入正式聚合接口，并同步更新 [LinkForty API 集成契约](./linkforty-api.md) 和 X-ANL-004 任务状态。当前不修改任务清单状态，不新增本地统计表或 Alembic 迁移。
