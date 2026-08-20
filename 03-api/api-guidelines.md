# API 规范

## 基本约定

- 路径统一使用 `/api/v1`。
- JSON 字段使用 camelCase，数据库字段使用 snake_case。
- BIGINT ID 在 JSON 中以字符串返回。
- 时间统一使用 ISO 8601 和时区。
- 写命令支持 `Idempotency-Key` 或请求体幂等键。
- 所有响应包含 `requestId`。

## 响应格式

```json
{
  "requestId": "trace-id",
  "data": {},
  "error": null
}
```

## 错误格式

```json
{
  "requestId": "trace-id",
  "error": {
    "code": "ASSIGNMENT_CONFLICT",
    "message": "触点载体已有有效绑定",
    "details": {}
  }
}
```

## 列表接口

统一支持 `page`、`pageSize`、`sortBy`、`sortOrder`。`sortBy` 必须使用服务端白名单，不能直接拼接客户端输入。

## 权限

每个接口必须定义功能权限和数据范围。前端按钮隐藏不能替代后端校验。

## 前端 API 消费约定

- 所有后台请求必须经过统一 API Client；页面和组件不得直接调用 `fetch`、`axios` 或拼装 URL。
- 领域 Service 位于 API Client 之上，Service 方法对应一个明确的领域操作；页面通过 Service 或 TanStack Query Hook 获取和修改数据。
- Query/Mutation 必须统一管理缓存键、缓存失效、重复提交和成功后的刷新行为。
- `requestId`、错误码、Envelope、BIGINT 字符串和 ISO 8601 时间格式沿用本文件的公共 API 约定。
- 通用 `Idempotency-Key` 的持久化、回放、TTL 和冲突语义以 `DEC-IDEMP-001` 为准；决策完成前，前端不得自行选择存储方案。
- 领域唯一键、Webhook `event_id`、资产/员工/组织稳定业务键和外部 LinkForty 幂等标识分别按各自领域契约执行，不用通用前端缓存替代数据库或外部系统事实。
- 前端隐藏菜单或按钮只改善用户体验，最终功能权限和数据范围必须由后台强制校验。
