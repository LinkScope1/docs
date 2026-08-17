# 部署架构

## 环境

```text
开发：本地 Python API + React + PostgreSQL + Redis + Mock
测试：容器化 Python API + React + PostgreSQL + Redis + 测试 Casdoor/LinkForty
预生产：接近生产的网络、权限和数据规模
生产：受限网络、独立账号、备份、监控和审批发布
```

## 服务

- `bank-admin-service`：Python FastAPI API。
- `bank-admin-worker`：Celery Worker。
- `bank-admin-web`：React 构建产物，由 Nginx 或网关提供。
- PostgreSQL：银行业务 Schema 和受限 LinkForty 读取。
- Redis：缓存和任务支撑。
- Casdoor：身份和功能权限。
- LinkForty Core：外部短链和事件平台。

## 网络原则

- 浏览器只访问网关或银行后台 API。
- 银行后台到 LinkForty API 使用服务间网络。
- 数据库不直接暴露公网。
- LinkForty 只读账号只授予白名单表和字段。
- 生产环境外部调用必须配置超时、TLS 和审计。
