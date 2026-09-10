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
- `bank-edge-nginx`：银行后台入口、LinkForty Core API 反向代理和 Webhook 转发。
- PostgreSQL：银行业务 Schema 和受限 LinkForty 读取。
- Redis：缓存和任务支撑。
- Casdoor：身份和功能权限。
- LinkForty Core：外部短链和事件平台。

## 网络原则

- 浏览器只访问网关或银行后台 API。
- 银行后台通过 Nginx 的 `/linkapi/` 反向代理调用 LinkForty Core；银行后台不得绕过 Nginx 直连 Core 或 Core 数据库。
- Nginx 使用私有网络、来源 ACL、防火墙、私有 DNS 和 HTTPS/TLS；LinkForty Core 管理/API 端口不暴露公网，只允许 Nginx/受控配置服务访问。
- Nginx 通过精确 `/api/v1/webhooks/linkforty` location 将 Core Webhook 转发到银行 API，并保留原始 body 与签名 Header；该链路不使用 API Key、JWT、OAuth 或 mTLS 客户端证书。
- 数据库不直接暴露公网。
- V1.3.2 的 LinkForty 读取通过 API-only 边界完成，不新增或使用 Core 数据库直连；后续只读账号若启用，仍只能授予白名单表和字段。
- 生产环境外部调用必须配置超时、TLS 和审计。

## LinkForty 代理拓扑

当前仓库提供的 Nginx 配置适用于测试拓扑：Nginx 在宿主机监听 `80`，Core Compose 服务
`linkforty` 的宿主机端口为 `127.0.0.1:3200`，银行测试 API 的宿主机端口为
`127.0.0.1:18000`。Docker 内的银行 API 使用 `host.docker.internal` 访问宿主机 Nginx，
不得使用容器内指向自身的 `127.0.0.1`。

如果 Nginx 与 Core 运行在同一 Docker 网络，才可以把 Core 上游改为已确认的服务名
`linkforty:3000`；当前两个 Compose 的默认网络彼此隔离，不能直接假设该名称跨 Compose 可达。
生产环境必须另行确认共享网络、私有 DNS、TLS 证书和 ACL，不能直接把测试监听和地址视为生产配置。

## Redis/Celery 隔离

- Redis 只承载 Broker、缓存和任务支撑，不是业务事实来源；业务唯一性和状态以 PostgreSQL 为准。
- API、Worker 和测试环境使用不同 Redis 实例或至少不同 DB、队列名和命名空间；测试任务不得消费生产队列。
- 生产建议 API 缓存、Celery Broker/Result 使用独立 Redis 实例，并为队列、连接和故障恢复设置独立监控。
- Redis 故障时不得丢失已提交的银行业务事实；任务失败只能进入重试/补偿和 M1 审计路径。

## LinkForty 网络隔离验收

- local 仅使用 Mock，不连接生产 Core；
- test 使用测试网段 ACL 和测试 Core；
- staging 使用预生产网段和预生产 Core；
- production 使用独立网段、独立 ACL、独立 Core 地址和审批变更；
- 非允许来源无法建立连接；允许来源必须通过 HTTPS/TLS 服务端证书校验。
