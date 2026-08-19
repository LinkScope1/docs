# 测试策略

## 测试层级

1. Pydantic Schema 单元测试。
2. 业务 Service 单元测试。
3. Repository 数据库测试。
4. FastAPI API 集成测试。
5. 外部集成 Mock 测试。
6. 权限和越权测试。
7. Webhook 并发幂等测试。
8. 前端组件测试。
9. Playwright 端到端测试。
10. 性能、安全和回滚测试。

## 必测场景

- JWT 错误、过期、缺少 `employee_code`、停用员工。
- 组织编码前缀校验和停用阻断。
- 编码重复。
- 非空 `carrier_uid` 重复。
- 绑定时间重叠。
- 绑定历史无名称快照且当前绑定唯一。
- LinkForty 超时和 5xx。
- Webhook 签名错误、重复和乱序。
- 统计机器人排除。
- 导出权限和审计。
- 文档导入更新、新增、显式解绑、幂等和逐行结果。
