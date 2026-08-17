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
