# 安全测试方案

- JWT 伪造和过期。
- issuer/audience 错误。
- 停用用户访问。
- API 权限缺失。
- 跨组织读取和写入。
- 导出越权。
- LinkForty 非允许网段连接被拒绝。
- LinkForty 允许网段 HTTPS/TLS 服务端证书校验。
- LinkForty 出站请求不携带 API Key、JWT 或 Token。
- Webhook 签名错误和重放。
- SQL 注入和排序注入。
- 敏感字段泄露。
- LinkForty 只读账号写入尝试。
- 审计日志篡改尝试。
