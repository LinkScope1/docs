# Casdoor OIDC BFF 集成契约

## 状态与边界

本文件描述银行后台的目标设计和可测试集成边界，不代表已连接真实 Casdoor，也不包含真实 Secret。`P0-CAS-001～006`、`DEC-CAS-001～006` 继续延期，未因 Fake、Mock、接口或单元测试完成而关闭。

Casdoor 是身份、角色和功能权限权威；M1 负责认证上下文、Session 和审计，M2 负责使用规范化 `employee_code` 查询本地 `employees` 及所属组织。银行后台不创建 `iam_*` 表，不复制 Casdoor 用户、角色或密码。

## 目标时序

1. 浏览器访问 `GET /api/v1/auth/login`。
2. FastAPI 生成不可预测的一次性 `state`、`nonce`，并使用 S256 PKCE。Redis 以 `bank-admin:auth:state:{state}` 保存 state、nonce 和时间元数据，TTL 默认 300 秒；生产环境使用服务端专用 `AUTH_STATE_SIGNING_KEY` 基于 state 派生 `code_verifier`，因此 verifier 不序列化到 Redis，开发/测试 Fake 可只在进程内保存。
3. FastAPI 302 到 Casdoor Authorization Endpoint；redirect URI 来自服务端配置，不信任请求参数。
4. Casdoor 回调 `GET /api/v1/auth/callback?code=...&state=...`。
5. FastAPI 使用 Redis 中的一次性 state 校验并立即删除记录，然后用服务端派生的 `code_verifier` 和 `code` 调用 Token Endpoint。
6. FastAPI 只在内存短暂持有 Token，并使用配置化 JWKS 校验 `id_token` 的签名、issuer、audience、subject、nonce、exp 和 60 秒时钟偏差。
7. 从规范化 Claims 读取 `employee_code`、角色和权限；缺失、类型错误、角色到数据范围映射缺失或歧义时 fail closed。
8. M2 Repository 按 `employee_code` 查询员工和组织；员工或组织不存在/停用时拒绝访问。
9. Redis 以 `bank-admin:auth:session:{session_id}` 创建短期 Session。Session 只保存 subject、employee_code、角色、权限、issued_at、expires_at，TTL 默认 1800 秒且不超过上游 Token 剩余有效期。
10. FastAPI 302 到固定配置的前端路径并设置 `bank_admin_session` Cookie。

失败回调只重定向到固定配置路径并带稳定错误码，不回显 Casdoor 原始错误、Token 或内部堆栈。当前 callback 是目标设计和本地可测试边界，不是外部联调证据。

## Token、Session 和 Cookie

- 浏览器不得直接请求 Casdoor Token Endpoint；前端不保存 `localStorage`/`sessionStorage` Token，也不发送 Bearer Token。
- `access_token`、`id_token`、`refresh_token`、密码、Secret 和 PKCE verifier 不写入数据库、Session、Cookie、日志或审计。生产环境的 PKCE verifier 由服务端专用密钥基于 state 派生，不序列化到 Redis；开发/测试 Fake 可仅在进程内短期保存，兑换完成或失败后删除。
- `id_token` 只用于身份声明，不能作为业务 API access token。
- Cookie 名称固定为 `bank_admin_session`，属性为 `HttpOnly`、`Path=/`、`SameSite=Lax`，生产环境必须 `Secure`。
- 带 Session Cookie 的 POST/PUT/PATCH/DELETE 必须校验允许的 `Origin`；不满足时返回 `AUTH_ORIGIN_NOT_ALLOWED`（403）。
- `/api/v1/auth/logout` 删除 Redis Session 并清理 Cookie，不调用未确认的外部注销接口。
- 每次业务请求仍按 `employee_code` 查询本地员工/组织；员工停用立即生效，角色变化最多延迟到 Session 过期。

## 待平台确认的配置

以下内容全部配置化，不猜测 Casdoor 默认值：

- Authorization Endpoint、Token Endpoint、JWKS URI、issuer、audience、client ID、redirect URI 和算法；
- 服务端 `AUTH_STATE_SIGNING_KEY`（仅用于派生 PKCE verifier，不提交到仓库或写入 Redis）；
- `employee_code` Claim 名称、类型和稳定性；
- 角色 Claim、权限 Claim、角色到 `GLOBAL`/组织/员工/资产数据范围的映射，以及 scope 映射策略；
- OIDC scope、员工停用同步策略、JWKS 轮换策略和平台时钟口径。

配置不完整时，生产环境使用 fail-closed Adapter，认证请求返回既有 `AUTH_INVALID_TOKEN`，不会退回 Mock 身份。

## 测试边界

默认单元测试使用 Fake OIDC Client、Fake/InMemory Session Store 和测试签名材料，不执行真实 Casdoor 网络请求、不使用真实 Secret。HTTPX 适配器、JWT/JWKS 缓存、未知 `kid` 强制刷新、state 一次性删除、员工/组织状态、Session TTL、Cookie 属性和 Origin 防护均可独立验证。
