# 系统架构

```text
bank-admin-web
React + TypeScript
        |
        v
bank-admin-service
Python + FastAPI
        |
        +-- PostgreSQL bank_admin schema
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
- M7/M8 只能只读指定 LinkForty 表。
- 不读取 `webhooks.secret`。
- 前端只能调用银行后台 API，不直接调用 LinkForty Core。

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

Celery 用于 Webhook 重试、LinkForty 发布补偿、预约绑定生效和对账。业务最终状态必须落 PostgreSQL，Redis 不能作为唯一事实来源。
