# API 规范

## 1. 基本约定

- 业务 API 路径统一使用 `/api/v1`。
- JSON 字段使用 `camelCase`，数据库字段使用 `snake_case`。
- PostgreSQL `BIGINT` 雪花 ID 在请求和响应 JSON 中均使用字符串，禁止按 JavaScript Number 传输。
- UUID 使用标准 UUID 字符串。
- 时间使用包含时区的 ISO 8601 字符串，例如 `2026-08-20T10:30:00+08:00`。
- 状态和类型字段使用文档定义的整数枚举值。
- 空集合返回 `[]`，可空单值返回 `null`，不得用空字符串代替空值。
- V1.3.2 写命令使用接口声明的领域幂等键、状态命令键或 `event_id`；通用 `Idempotency-Key` 响应回放延期到 V1.4。
- HTTP 状态码表达请求结果，响应体不重复增加 `success` 或数字成功码。

## 2. Request ID

- 每次请求必须有 `requestId`。
- 调用方提供合法 `X-Request-ID` 时后端沿用；未提供时由后端生成。
- 响应头 `X-Request-ID` 必须与响应体 `requestId` 完全一致。
- `requestId` 用于关联应用日志、操作审计、外部调用和异步任务，不得作为业务幂等键。

## 3. 成功响应

单对象、创建、修改、启停、绑定和解绑等有返回数据的成功响应统一为：

```json
{
  "requestId": "01JABCDEF123456789",
  "data": {
    "id": "1985623456789012480",
    "orgCode": "1001",
    "orgName": "测试分行",
    "status": 1
  }
}
```

- 查询和修改成功通常返回 `200 OK`。
- 创建成功返回 `201 Created`。
- 异步任务受理成功返回 `202 Accepted`。
- 无正文的删除操作可以返回 `204 No Content`；该状态不得携带 JSON 响应体。
- 本系统原则上使用启停、作废或解绑保留历史，优先返回操作后的对象，不使用物理删除。
- 成功响应不返回 `error: null`。

## 4. 分页列表响应

组织、员工、载体、载体内容、绑定、访问事件和操作日志列表统一返回：

```json
{
  "requestId": "01JABCDEF123456789",
  "data": {
    "items": [],
    "page": 1,
    "pageSize": 20,
    "total": 0
  }
}
```

- `page` 从 `1` 开始，默认值为 `1`。
- `pageSize` 默认值为 `20`，最小值为 `1`，最大值为 `100`。
- `total` 是应用数据范围和筛选条件生效后的总记录数。
- 无匹配数据时 `items` 必须返回 `[]`，不得返回 `null`。
- `totalPages`、`hasNext` 和 `hasPrevious` 由调用方计算，当前契约不重复返回。
- `sortBy` 只能使用接口声明的服务端白名单；禁止将客户端输入直接拼接到 SQL。
- `sortOrder` 只接受 `asc` 或 `desc`。

固定枚举等无需分页的小集合使用：

```json
{
  "requestId": "01JABCDEF123456789",
  "data": {
    "items": [
      {"value": 0, "label": "停用"},
      {"value": 1, "label": "启用"}
    ]
  }
}
```

## 5. 错误响应

业务错误统一返回：

```json
{
  "requestId": "01JABCDEF123456789",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "组织不存在"
  }
}
```

参数校验错误可以增加可选的 `details`：

```json
{
  "requestId": "01JABCDEF123456789",
  "error": {
    "code": "REQUEST_SCHEMA_INVALID",
    "message": "请求参数校验失败",
    "details": [
      {"field": "query.limit", "type": "int_parsing", "message": "输入应为有效整数"},
      {"field": "orgName", "type": "missing", "message": "字段为必填项"}
    ]
  }
}
```

- 错误响应不返回 `data: null`。
- `details` 为可选数组，仅用于返回可公开的字段级校验信息。
- 不得返回堆栈、SQL、数据库连接信息、密码、Token、JWT、Webhook Secret 或其他敏感信息。
- 未预期异常对外统一返回 `INTERNAL_ERROR`，详细异常只写入脱敏后的服务端日志。

## 6. HTTP 状态码

| 状态码 | 使用场景 |
| --- | --- |
| `200` | 查询、修改、启停、绑定或解绑成功 |
| `201` | 创建成功 |
| `202` | 异步任务已受理 |
| `204` | 操作成功且无响应正文 |
| `400` | 请求业务格式或逻辑错误 |
| `401` | 未认证、Token 无效或过期 |
| `403` | 功能权限不足或超出数据范围 |
| `404` | 业务对象不存在 |
| `409` | 唯一性、当前绑定或状态转换冲突 |
| `422` | 请求字段类型、必填项等结构校验失败 |
| `500` | 未预期的系统异常 |
| `502` | LinkForty 等外部服务返回异常 |
| `503` | 本系统或依赖服务暂时不可用 |
| `504` | 外部调用超时 |
| `413` | 同步导出超过 10 MiB 或 100,000 行限制 |

`501 Not Implemented` 只用于尚未实现的工程占位接口；正式实现后必须删除对应占位行为和测试。

## 7. 错误码规范

- 错误码使用稳定的英文大写蛇形命名，不使用中文、连续数字编号或临时异常文本。
- 相同业务错误在 M1–M5 中必须使用同一错误码。
- 修改面向用户的中文 `message` 不得改变 `code` 的业务含义。
- [错误码清单](./error-codes.md) 是 M1–M5 唯一的错误码及 HTTP 映射来源；本文件不重复维护第二份清单。
- 模块新增错误码时必须先更新错误码清单，并同步更新 OpenAPI 和测试，不得在 Router 中临时拼接错误结构。

## 7.1 统计汇总契约

`GET /api/v1/analytics/summary` 只返回 `clickCount`、`accessCount`、`installCount` 和 `inAppCount` 四项汇总计数，以及 `from`、`to` 和可选的 `orgCodePrefix`。

- 访问使用本地 `access_events.received_at`；LinkForty 点击统计通过 API 获取，Core 负责排除机器人。安装和 App 事件仍沿用目标事件时间口径，但当前 Core API 未提供对应聚合读取接口，不能通过数据库直连补齐。
- `orgCodePrefix` 只能在 `AccessContext` 已授权范围内进一步收窄；不能通过请求参数扩大数据范围。
- 任一必要数据源不可用时返回 `503 DATA_SOURCE_UNAVAILABLE`，不返回部分成功的统计结果。
- 统计不创建本地专属表，不返回趋势数组、未经确认的统计维度或银行业务办理量。
- V1.3.2 只允许 API-only 外部读取；LinkForty 数据库只读账号、SQL 白名单和负向权限测试延期至 V1.4。

## 8. 权限和数据范围

- 每个接口必须定义功能权限和组织、员工数据范围。
- 前端按钮隐藏不能替代后端权限校验。
- 前端传入的 `orgId`、`employeeId` 和筛选条件不得扩大当前访问上下文的数据范围。
- 逻辑外键的存在性、状态和归属关系由 Service 在同一业务事务内校验。
