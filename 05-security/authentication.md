# 认证与会话安全

## 目标方案

银行后台采用 Authorization Code + PKCE（S256）+ FastAPI BFF + Redis 服务端 Session + HttpOnly Cookie。浏览器只访问银行后台的 `/api/v1/auth/login`，不直接请求 Casdoor Token Endpoint。

```text
Browser -> FastAPI /auth/login
FastAPI -> Redis: state + nonce + 时间元数据（300s）；PKCE verifier 由服务端密钥派生，不序列化到 Redis
FastAPI -> Casdoor Authorization Endpoint
Casdoor -> FastAPI /auth/callback?code&state
FastAPI -> Casdoor Token Endpoint: 服务端 code exchange
FastAPI -> JWKS: 校验 id_token
FastAPI -> M2 employees: employee_code + 启用状态
FastAPI -> Redis: normalized session（最多 1800s）
FastAPI -> Browser: 302 到 AUTH_FRONTEND_BASE_URL + 固定路径；bank_admin_session（HttpOnly）
```

`state`、`nonce`、`code_verifier` 只在服务端短期使用。state 使用 `bank-admin:auth:state:{state}`、TTL 300 秒，callback 无论成功或失败都必须一次性删除；Redis state 记录不包含 PKCE verifier，生产环境由服务端专用 `AUTH_STATE_SIGNING_KEY` 基于 state 派生 verifier，开发/测试 Fake 可在内存保存 verifier。Session 使用 `bank-admin:auth:session:{session_id}`。回调不接受前端跳转地址，成功和失败只重定向到服务端配置的 `AUTH_FRONTEND_BASE_URL` 加固定相对路径；该基础地址必须与 `FRONTEND_ORIGINS` 中的允许 Origin 匹配。本机开发地址为前端 `http://localhost:5173`、后端 `http://localhost:8000`。

## Token 与 JWT 边界

- access token、id token、refresh token 只在 FastAPI 内存中短暂用于兑换和校验，不写入数据库、Redis Session、Cookie、日志、审计或错误响应。
- `id_token` 只用于身份声明，不能作为业务 API access token。
- JWT 必须校验签名、配置化 issuer、audience、非空 subject、nonce、exp 和 60 秒时钟偏差；未知 `kid` 强制刷新 JWKS 后只重试一次。
- `employee_code`、角色 Claim、权限 Claim、算法、issuer、audience、JWKS URI、scope 和角色到数据范围映射均配置化。未获 Casdoor 平台证据前不得猜测默认 Claim 或权限编码；映射不明确时拒绝访问。
- `AUTH_STATE_SIGNING_KEY` 是服务端密钥管理项，仅用于从一次性 state 派生 PKCE verifier；它不进入响应、日志、审计、Cookie、数据库或 Redis。

## Session 与 Cookie

Redis Session 只保存：subject、employee_code、角色、权限、issued_at、expires_at。默认 TTL 为 1800 秒且不得超过上游 Token 剩余有效期。每次业务请求仍使用 `employee_code` 查询 M2 员工和所属组织；员工不存在、停用或组织停用立即拒绝。角色变化最多延迟到 Session 过期。

Cookie 名称固定为 `bank_admin_session`，必须设置 `HttpOnly`、`Path=/`、`SameSite=Lax`，生产环境必须设置 `Secure`。携带 Session Cookie 的 POST、PUT、PATCH、DELETE 必须校验允许的 `FRONTEND_ORIGINS`；缺失或不匹配返回 `AUTH_ORIGIN_NOT_ALLOWED`（403）。登出删除服务端 Session 并清理 Cookie，不调用未确认的外部注销接口。

## M1/M2 职责边界

- Casdoor：身份、角色和功能权限权威，不向本地复制用户/角色表。
- M1：认证上下文、Session、`/auth/me` 和操作审计；业务层唯一入口是 `AccessContext`、`require_permission`、`authorize`。
- M2：通过 `employee_code` 查询本地员工和所属组织，提供员工/组织启停事实。
- M3～M5：只消费规范化 `AccessContext`，不解析 JWT、不调用 Casdoor、不读取 Cookie 原文。
- 不新增 M6，不创建 `iam_*` 表，不修改 LinkForty Core、`core/` 目录或 LinkForty 数据库。

## 失败关闭与外部契约状态

生产未配置完整真实 Casdoor 时，Adapter fail closed，认证请求返回既有 `AUTH_INVALID_TOKEN`，不回退到 Mock 身份。callback 错误只返回稳定错误码，不泄漏 Casdoor 原始错误或堆栈。

真实 Casdoor issuer、audience、JWKS URI、算法、Claim、角色/权限编码、员工停用同步、轮换策略和时钟口径仍待平台确认。`/auth/callback` 当前属于目标设计和本地测试边界，不得宣称真实外部认证联调完成；`P0-CAS-001～006`、`DEC-CAS-001～006` 继续延期。

## 验证要求

默认单元测试使用 Fake OIDC、Fake/InMemory Session Store 和测试密钥，不访问真实 Casdoor、不使用真实 Secret。必须覆盖 state 一次性、PKCE、JWT/JWKS、Claim/员工/组织停用、Session TTL/logout、Cookie 属性、Origin、权限/数据范围、`/auth/me` 回归和 Token/密码/Secret 脱敏。
