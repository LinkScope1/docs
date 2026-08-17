# 数据流和时序

## 登录和权限

```text
Browser -> Casdoor: OIDC 登录
Casdoor -> Browser/Backend: JWT 或授权回调
Backend -> Casdoor JWKS: 验证签名
Backend -> bank_admin: 查询 iam_users 和数据范围
Backend -> Browser: 认证上下文
```

## 路由发布

```text
前端 -> M6: 提交规则和发布确认
M6 -> M5: 校验目标资源
M6 -> LinkForty API: 发布目标配置
LinkForty API -> M6: 返回结果
M6 -> bank_admin: 更新 publish_status 和 operation_logs
```

## 访问事件

```text
LinkForty -> M7 Webhook: 发送签名事件
M7 -> access_events: event_id 幂等写入
M7 -> LinkForty 只读数据: 读取点击事实
M7 -> M3/M4/M6 数据: 按事件时间读取快照
M7 -> access_events: 写入关联结果和解析状态
```
