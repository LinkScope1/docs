# 环境清单

| 环境 | 用途 | 数据 | 外部系统 | LinkForty 网络边界 | 发布方式 |
|---|---|---|---|---|---|
| local | 个人开发 | Mock/本地测试 | Mock 或开发实例 | 仅 Mock，不连接生产 Core | 本地命令 |
| test | 自动化和集成测试 | 测试数据 | 测试 Casdoor/LinkForty | 测试网段 ACL、私有 DNS、HTTPS/TLS | CI/CD |
| staging | 预生产验证 | 脱敏测试数据 | 预生产外部系统 | 预生产网段 ACL、私有 DNS、HTTPS/TLS | 审批发布 |
| production | 真实业务 | 生产数据 | 生产外部系统 | 独立网段、独立 ACL、私有 DNS、HTTPS/TLS 和变更审批 | 变更审批 |

生产配置、密钥和真实数据不得提交到仓库。

银行后台直连 LinkForty Core，不经过 API 网关；LinkForty Core 管理 API 不暴露公网，不使用 API Key、JWT、OAuth 或 mTLS 客户端证书。非允许来源必须无法建立连接。
