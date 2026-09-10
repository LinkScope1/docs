# LinkForty Webhook 契约

## 状态

已确认：本地真实样例和 LinkForty 负责人正式契约确认均已完成。

- 确认日期：2026-08-21
- 确认范围：签名算法和 Header、原始 body 计算方式、事件字段路径、事件标识语义、事件时间和重试契约
- 确认记录未包含 Secret、完整 payload 或个人敏感信息

## 与 LinkForty API 的安全边界

- 银行后台调用 LinkForty Core：通过 Nginx `/linkapi/`，并由私有网络、来源 ACL、防火墙、私有 DNS 和 HTTPS/TLS 保护，不使用应用层认证；
- LinkForty Core 调用银行 Webhook：必须使用 HMAC-SHA256 签名；
- Webhook 验签失败不得进入业务处理。

## Webhook Nginx 转发

Core 的 Webhook URL 使用 Nginx 暴露的
`POST /api/v1/webhooks/linkforty`。Nginx 将该精确路径转发到银行 API 的同一路径，不
重写、格式化或缓存 body，并保留 `X-LinkForty-Signature`、`X-LinkForty-Event` 和
`X-LinkForty-Event-ID`。银行应用继续以原始 bytes 执行 HMAC-SHA256 验签，再按
`event_id` 做幂等处理。

## Secret provisioning（当前最终方案）

Webhook 签名 Secret 按 LinkForty `webhooks` 配置记录生成，不按单次事件生成。同一订阅端点的多个事件和重试复用该记录对应的 Secret；不同订阅端点使用不同 Secret。

当前沿用 LinkForty Core 已有管理 API，不新增 provisioning 接口：

1. 银行后台配置服务通过 Nginx `/linkapi/api/webhooks` 调用 `POST /api/webhooks` 创建订阅，并从响应取得该订阅记录的 Secret。
2. 已存在的订阅可由受控配置流程通过 Nginx `/linkapi/api/webhooks/:id` 调用 `GET /api/webhooks/:id` 一次性读取 Secret。
3. Secret 写入银行后台受保护的运行时配置，不写入银行 7 张业务表，不进入前端、日志、审计、fixture 或文档。
4. 后续 Webhook 事件由银行后台使用本地验签配置处理；事件接收和重试期间不再调用 Core 获取 Secret。

上述创建/读取只允许银行后端配置服务执行，不允许浏览器或普通业务 API 代办。当前 Core 管理 API 不使用应用层认证，访问前必须满足 Nginx 私有网络、来源 ACL、防火墙、私有 DNS、HTTPS/TLS 和网络审计条件；配置服务联调、网络访问审计和生产配置接入仍是待实施事项。

该 provisioning API 交互不授权银行后台直接读取 LinkForty 数据库；`bank_linkforty_ro` 仍不得读取 `webhooks` 或 `webhooks.secret`。

## 已确认的契约项目

- 签名算法。
- 签名 Header。
- 原始载荷计算方式。
- `event_id` 位置和格式。
- `click_id` 位置和格式。
- 事件时间字段。
- 重试间隔和次数。
- 最终失败状态。

签名、字段和重试契约已由负责人确认；密钥不得进入代码、fixture、日志或文档。

## 本地真实样例观察结果（2026-08-21）

- Core 版本：`1.21.0`；通过真实短链访问触发 `click_event`，不是调用测试投递接口。
- 签名：`X-LinkForty-Signature: sha256=<64位十六进制字符>`，银行接收端使用原始 body 完成 HMAC-SHA256 验证。
- 字段路径：`event`、`event_id`、`timestamp`、`data.id`（`click_id`）、`data.linkId`（LinkForty Link UUID）。
- 真实 body SHA-256：`29b71f9eb0a8989b9af32533ea944cd489ec856a34c6d4b29c3cb38c564dfc43`。
- 接收结果：HTTP 202；重复完整请求幂等成功；body 或签名篡改返回 401；缺少 `event_id` 返回 400。
- 重试观察：一次性探针第一次返回 500，约 1.027 秒后收到第二次请求并返回 202。
- 脱敏报告位于仓库外受控目录 `/private/tmp/linkforty-webhook-evidence/verification-report.json`；不含 Secret 或完整 payload。

## 银行后台处理

1. 接收原始请求。
2. 验证签名。
3. 验证 `event_id`。
4. 使用数据库唯一约束执行幂等。
5. 读取点击事实。
6. 通过 Payload 关联触点资产。
7. 按事件时间读取绑定，并确定事件责任组织和员工。
8. 写入 `access_events`。
9. 记录解析状态和失败原因。

## 幂等

- 缺少 `event_id`：拒绝。
- 签名错误：拒绝。
- 重复 `event_id`：幂等成功。
- 相同 `click_id` 不同 `event_id`：允许保存。

V1.3.2 不执行目标资源解析或路由发布；事件表不保存路由和目标资源字段。

## 工作区实现

银行后台接收地址为 `POST /api/v1/webhooks/linkforty`。实现位于 `bank-touchpoint-backend/src/app/integrations/linkforty/webhook.py` 和 `src/app/modules/events/`：

- 使用原始请求 bytes 计算 HMAC-SHA256，并使用常量时间比较；
- 兼容当前 LinkForty Core 的 `event`、`event_id`、`timestamp`、`data` envelope；
- 校验 body 与 `X-LinkForty-Event`、`X-LinkForty-Event-ID` 的一致性；
- 按 `linkforty_link_id` 查找银行载体内容，按事件时间匹配历史绑定；
- 通过 `access_events.event_id` 唯一约束处理重复投递；
- 仅在显式配置受控 `WEBHOOK_EVIDENCE_DIR` 时保存原始 body 和脱敏元数据。

当前已完成本地真实点击投递、证据验证和 LinkForty 负责人正式确认；本文件可作为当前 Webhook 契约基线。
