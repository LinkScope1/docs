# V1.3.2 数据流和时序

## 登录和权限

```text
Browser -> Casdoor: OIDC 登录
Casdoor -> Browser/Backend: JWT
Backend -> Casdoor JWKS: 验证签名、issuer、audience 和过期时间
Backend -> bank_admin: 用 employee_code 查询 employees
Backend -> Browser: 员工、组织和有效数据范围
```

银行库不保存 Casdoor 用户、角色或权限投影。Casdoor 负责功能权限，银行后台按员工所属组织和业务表的 `org_id`、`employee_id` 做数据范围过滤。

## 触点和绑定

```text
前端 -> M2/M3/M4: 组织、员工、资产、内容和绑定命令
M4 -> bank_admin: 追加绑定历史
M4 -> M3: 提交资产和内容责任范围同步命令
M4 -> M1: 提交审计上下文
M1 -> operation_logs: 写入操作审计
```

## LinkForty 外部调用

```text
M3 -> LinkForty API: 私有网络 + ACL + HTTPS/TLS 直连；无应用层认证
M3 -> Worker: 提交需要重试或补偿的任务
Worker -> LinkForty API: 执行重试和补偿
M3/Worker -> M1: 提交调用结果、trace_id 和错误摘要
M1 -> operation_logs: 记录成功、失败或部分成功
```

银行后台到 LinkForty Core 不经过 API 网关或其他中间代理。`issuer`、`audience`、`subject` 和 API Credential 对该出站链路不适用；银行后台面向浏览器的业务 API 仍使用 Casdoor JWT。

`touchpoint_payloads` 只保存 `linkforty_link_id` 等必要逻辑引用，不保存 LinkForty 专属同步状态。

## 访问事件

```text
LinkForty -> M5 Webhook: 发送签名事件
M5 -> access_events: event_id 幂等写入
M5 -> LinkForty 只读数据: 读取点击事实
M5 -> M3/M4 数据: 关联资产、绑定、组织和员工
M5 -> access_events: 写入关联结果和状态
```

V1.3.2 不包含目标资源解析和路由发布流程。
