# 安全开发规范

- 所有外部输入必须验证。
- 所有数据库查询使用参数化查询。
- 所有排序字段使用白名单。
- 所有外部 HTTP 调用设置超时。
- 所有 Webhook 验签后才进入业务处理。
- 银行后台至 LinkForty Core 使用私有网络、来源 ACL、防火墙、私有 DNS 和 HTTPS/TLS；该链路不使用应用层 API Key、JWT、OAuth 或 mTLS 客户端证书。
- LinkForty Core 管理 API 不得暴露公网；网络隔离例外必须经过安全审批并接受网络区域内服务被冒用的风险。
- 所有关键命令记录审计。
- 日志不得输出密码、Token、JWT 或 Secret。
- 导出必须校验权限和数据范围。
- LinkForty 只读账号不得读取 `webhooks.secret`。
- 生产密钥只能通过密钥管理或环境注入。
- 生产数据不得直接复制到开发环境。
