# 日志规范

## 统一字段

```text
timestamp
level
service
environment
request_id
trace_id
operator_id
operation_id
event_id
click_id
external_request_id
celery_task_id
error_code
```

## 禁止记录

- 密码。
- JWT。
- Token。
- Webhook Secret。
- 数据库密码。
- 未脱敏个人信息。

业务失败、运行异常、审计记录和安全告警必须区分，不得全部混写为普通日志。
