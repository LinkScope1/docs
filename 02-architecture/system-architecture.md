# 系统架构

```text
bank-admin-web
React + TypeScript
        |
        v
bank-admin-service
Python + FastAPI
        |
        +-- PostgreSQL bank_admin schema: 7 V1.3.2 tables
        +-- Redis + Celery
        +-- Casdoor
        +-- LinkForty API（私有网络 + ACL + HTTPS/TLS；无应用层认证）
        +-- LinkForty PostgreSQL read-only access
        |
        v
LinkForty Core
TypeScript + Fastify
```

## 边界

- 银行后台服务写银行业务表。
- LinkForty 写入必须走 LinkForty API。
- 银行后台直接通过私有网络调用 LinkForty Core，不经过 API 网关或其他中间代理。
- LinkForty Core 管理 API 仅允许银行后台服务网段访问，不暴露公网；该链路不使用 API Key、JWT、OAuth 或 mTLS 客户端证书。
- Webhook 配置由银行后台配置服务在创建或恢复配置时调用 Core 现有管理 API 一次性 provisioning；不按事件运行时调用 Core。
- M5 和非编号统计与报表能力只能只读 `docs/04-database/db-permissions.md` 白名单中的 LinkForty 表和必要字段。
- 银行后台不得通过 LinkForty 数据库直读 `webhooks.secret`；受控 API provisioning 只向配置服务一次性交付验签运行时配置。
- 前端只能调用银行后台 API，不直接调用 LinkForty Core。
- 银行库不创建 `iam_*` 表；Casdoor 角色和功能权限不复制到本地。
- V1.3.2 暂不建设目标资源和路由规则。M3 通过 LinkForty API 发起外部调用，M1 负责结果审计。

Webhook Secret provisioning 方案已确认，但配置服务自动接入、网络访问审计和生产配置接入尚未完成；该决策不等同于 M5 业务功能已全部实现。

## 后端分层

```text
API Router
  -> Auth/Data Scope Dependencies
  -> Application Service
  -> Domain Rules
  -> Repository / Integration
  -> PostgreSQL / External API
```

## 异步任务

Celery 用于 Webhook 重试、LinkForty 外部调用补偿、预约绑定生效和对账。重试与补偿结果通过 `operation_logs` 和 `trace_id` 追踪，不在 `touchpoint_payloads` 中建立同步状态机；Redis 不能作为唯一事实来源。
