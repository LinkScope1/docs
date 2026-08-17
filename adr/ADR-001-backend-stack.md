# ADR-001：后端采用 Python FastAPI

## 状态

Accepted

## 决策

银行后台采用 Python 3.11+、FastAPI、Pydantic、SQLAlchemy、Alembic 和 PostgreSQL。

## 原因

- 设计文档已有 Python/FastAPI 实施约定。
- MVP 以后台管理、外部集成和统计查询为主。
- FastAPI 可提供 OpenAPI 和请求模型校验。
- 当前团队已确定 Python 后端方向。

## 影响

- 必须执行严格类型检查、分层和测试规范。
- 生产环境需要明确 Python 服务的运行、监控和依赖升级方案。
- 不同时建设 Java 银行后台。

## 复查条件

只有在银行生产平台强制要求 Java/Spring 或团队运维能力无法支持 Python 时重新评估。
