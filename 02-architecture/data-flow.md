# V1.3.2 数据流和时序

## 登录和权限

```text
Browser -> FastAPI: GET /api/v1/auth/login
FastAPI -> Redis: 保存一次性 state、nonce 和时间元数据（TTL 300s）；PKCE verifier 由服务端密钥派生，不序列化到 Redis
FastAPI -> Casdoor: Authorization Code + PKCE(S256) 授权请求
Casdoor -> FastAPI: GET /api/v1/auth/callback?code&state
FastAPI -> Casdoor: 服务端 Token Exchange（code + code_verifier）
FastAPI -> Casdoor JWKS: 验证 id_token 签名、issuer、audience、subject、nonce、exp
FastAPI -> bank_admin: 用 employee_code 查询启用 employees 和组织
FastAPI -> Redis: 保存规范化 Session（TTL <= 1800s 且不超过上游 Token 剩余时间）
FastAPI -> Browser: 302 + HttpOnly bank_admin_session Cookie
Browser -> FastAPI: 业务请求携带 Cookie
FastAPI -> Browser: GET /api/v1/auth/me 返回员工、组织、角色、权限和数据范围
```

浏览器不直接请求 Casdoor Token Endpoint，也不接收原始 `access_token`、`id_token` 或 `refresh_token`。Token 只在 FastAPI 内存中短暂用于兑换和校验；Token、密码、Secret 和 PKCE verifier 不进入数据库、Session、Cookie、日志或审计（生产环境的 verifier 由服务端专用密钥基于 state 派生，不序列化到 Redis）。

银行库不保存 Casdoor 用户、角色或权限投影。Casdoor 是身份、角色和功能权限权威；M1 负责认证上下文、Session 和操作审计，M2 负责按 `employee_code` 查询本地员工及所属组织，业务模块只依赖 `AccessContext`、`require_permission` 和 `authorize`。员工或组织停用在下一次请求立即生效；角色变化最多延迟到 Session 过期。

回调只允许重定向到服务端配置的固定前端路径，不接受请求参数跳转地址。真实 Casdoor issuer、audience、JWKS URI、角色/权限 Claim 和停用同步策略仍待平台确认；上述 `/auth/callback` 是目标设计与本地可测试边界，不代表真实 Casdoor 联调完成。

Session Cookie 名称固定为 `bank_admin_session`，设置 `HttpOnly`、`Path=/`、`SameSite=Lax`，生产环境设置 `Secure`。携带 Cookie 的 POST/PUT/PATCH/DELETE 必须匹配配置的 `FRONTEND_ORIGINS`，否则返回 `AUTH_ORIGIN_NOT_ALLOWED`（403）。登出删除 Redis Session 并清理 Cookie，不调用未确认的外部注销接口。

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

银行后台到 LinkForty Core 不经过 API 网关或其他中间代理。`issuer`、`audience`、`subject` 和 API Credential 对该出站链路不适用；银行后台面向浏览器的业务 API 使用 BFF Session Cookie，Casdoor JWT 只在 FastAPI 服务端兑换和验证阶段短暂存在。

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
