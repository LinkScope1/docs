# 后端分层规范

## Router

负责 HTTP 参数、认证依赖、响应模型和状态码。

## Service

负责业务规则、事务、状态变化、审计和任务调度。

## Repository

负责 SQLAlchemy 查询和持久化，不决定业务权限和最终状态。

## Integration

负责 Casdoor、LinkForty、NFC 等外部系统调用、字段转换、超时和错误映射。

## Worker

负责重试、补偿和对账，不直接绕过 Service 修改业务状态。
