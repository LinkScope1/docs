# 安全测试清单

- [ ] JWT 伪造被拒绝
- [ ] JWT 过期被拒绝
- [ ] issuer 错误被拒绝
- [ ] audience 错误被拒绝
- [ ] 停用用户被拒绝
- [ ] 无权限接口被拒绝
- [ ] 跨组织查询被拒绝
- [ ] 跨组织写入被拒绝
- [ ] 导出越权被拒绝
- [ ] LinkForty 非允许网段无法建立连接
- [ ] LinkForty 允许网段可通过 HTTPS/TLS 服务端证书校验访问
- [ ] LinkForty 请求不携带 API Key、JWT 或 Token
- [ ] Webhook 签名错误被拒绝
- [ ] Webhook 重放不会重复入库
- [ ] 日志无敏感信息
- [ ] LinkForty 只读账号无法执行写操作
- [ ] 普通用户不能修改审计日志
