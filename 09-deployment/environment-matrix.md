# 环境清单

| 环境 | 用途 | 数据 | 外部系统 | LinkForty/Nginx 网络边界 | 发布方式 |
|---|---|---|---|---|---|
| local | 个人开发 | Mock/本地测试 | Mock 或开发实例 | 不配置代理，不连接生产 Core | 本地命令 |
| test | 自动化和集成测试 | 测试数据 | 测试 Casdoor/LinkForty | 银行 API 容器 → 宿主机 Nginx `/linkapi/` → `127.0.0.1:3200`；测试 ACL、私有 DNS、HTTPS/TLS | CI/CD |
| staging | 预生产验证 | 脱敏测试数据 | 预生产外部系统 | 银行后台仅经 Nginx；预生产 ACL、私有 DNS、HTTPS/TLS；Core 不公网暴露 | 审批发布 |
| production | 真实业务 | 生产数据 | 生产外部系统 | 独立 Nginx、独立网段/ACL、私有 DNS、HTTPS/TLS、网络审计；Core 不公网暴露 | 变更审批 |

生产配置、密钥和真实数据不得提交到仓库。

银行后台统一通过 Nginx 反向代理调用 LinkForty Core；LinkForty Core 管理 API 不暴露公网，不使用 API Key、JWT、OAuth 或 mTLS 客户端证书。非允许来源必须无法建立连接。当前仓库的 Nginx 配置仅适用于测试宿主机端口拓扑，生产地址、DNS、TLS、ACL 和 Secret 必须由运维注入并审批。
