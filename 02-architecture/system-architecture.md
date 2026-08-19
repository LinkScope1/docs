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
        +-- LinkForty API
        +-- LinkForty PostgreSQL read-only access
        |
        v
LinkForty Core
TypeScript + Fastify
```

## 边界

- 银行后台服务写银行业务表。
- LinkForty 写入必须走 LinkForty API。
- M5 和非编号统计与报表能力只能只读 `docs/04-database/db-permissions.md` 白名单中的 LinkForty 表和必要字段。
- 不读取 `webhooks.secret`。
- 前端只能调用银行后台 API，不直接调用 LinkForty Core。
- 银行库不创建 `iam_*` 表；Casdoor 角色和功能权限不复制到本地。
- V1.3.2 暂不建设目标资源和路由规则。M3 通过 LinkForty API 发起外部调用，M1 负责结果审计。

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
