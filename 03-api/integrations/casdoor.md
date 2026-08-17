# Casdoor 集成契约

## 状态

待外部平台确认。

## 必须确认

- issuer
- audience
- JWKS URI
- subject 格式
- 角色和权限编码
- 用户停用同步方式
- JWKS 轮换策略
- 时钟偏差容忍范围

## 后端行为

1. 获取并缓存 JWKS。
2. 校验 JWT 签名。
3. 校验 issuer、audience、subject 和过期时间。
4. 将 subject 映射到 `iam_users`。
5. 用户停用时拒绝访问。
6. 使用本地投影完成 API 映射和组织数据范围。

## 禁止

- 保存密码。
- 保存 Token。
- 本地另建身份权威。
- 用前端菜单代替后端权限。
