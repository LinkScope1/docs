# 部署手册

## 部署顺序

1. 检查数据库备份。
2. 检查 Nginx、Core 和银行 API 的网络连通性、TLS 证书及来源 ACL。
3. 安装并检查银行后台 Nginx 配置，再执行 `nginx -t`。
4. 执行银行侧 Alembic 迁移。
5. 部署 Python API。
6. 部署 Celery Worker。
7. 部署前端静态资源。
8. 检查银行 API `/health` 和 `/health/ready`。
9. 执行 Core 代理、Webhook 和业务冒烟测试。
10. 观察日志、指标和错误率。

## 当前测试拓扑

仓库中的 `bank-touchpoint-backend/nginx/bank-touchpoint-backend.conf` 是宿主机 Nginx
测试配置：Nginx 监听 `80`，Core 使用宿主机 `127.0.0.1:3200`，银行测试 API 使用
`127.0.0.1:18000`。银行 API/Worker 容器访问 Nginx 时使用
`host.docker.internal`，不能使用容器内的 `127.0.0.1`。

配置应使用：

```env
LINKFORTY_BASE_URL=https://links.example.com/linkapi
LINKFORTY_SHORT_LINK_BASE_URL=https://links.example.com/linkapi
```

以上域名只是示例，实际测试/生产地址由运维注入。Webhook Secret 只能由运行时 Secret
管理系统注入，禁止写入仓库、日志、fixture 或文档。

## Docker Nginx 变体

若 Nginx 与 Core 运行在同一共享 Docker 网络，可把 Core 上游改为
`proxy_pass http://linkforty:3000/;`。`linkforty` 是当前 Core Compose 已确认的服务名；
当前 Core 和银行测试 Compose 默认网络隔离，必须先由运维建立共享网络，不能直接套用该变体。

Core API 端口不得公网暴露；生产必须使用 HTTPS/TLS、私有 DNS、Nginx/网络 ACL、防火墙
和网络审计。当前仓库配置仅覆盖测试拓扑，不构成生产部署配置。

## 代理验证

```bash
nginx -t
curl -i http://127.0.0.1/linkapi/health/ready
curl -i http://127.0.0.1/linkapi/api/links
curl -i -X POST http://127.0.0.1/api/v1/webhooks/linkforty \
  --data-binary @/secure/evidence/request.body \
  -H 'Content-Type: application/json' \
  -H 'X-LinkForty-Signature: sha256=<runtime-generated-signature>' \
  -H 'X-LinkForty-Event: click_event' \
  -H 'X-LinkForty-Event-ID: <runtime-event-id>'
```

Webhook 冒烟请求中的 body、签名和 event ID 必须由测试环境在运行时生成，不能把 Webhook Secret 写入命令、仓库或日志。

`/linkapi/api/links` 返回 Core 的认证或业务错误仍表示请求已到达 Core；Webhook 冒烟
必须使用受控运行时 Secret 生成签名，不得把签名 Secret 或完整敏感 body 写入仓库。

## 禁止

- 未备份数据库前执行生产迁移。
- 直接修改生产表。
- 使用未审查的镜像或构建产物。
- 直接部署未通过 CI 的分支。
- 不得绕过 Nginx 直连 LinkForty Core 或访问 Core 数据库。
