# Python 后端开发规范

## 技术栈

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x Async
- asyncpg
- Alembic
- HTTPX
- Redis + Celery
- pytest + pytest-asyncio
- Ruff + mypy

## 目录职责

```text
api/             HTTP Router
schemas/         Pydantic 请求和响应模型
services/        业务规则和事务编排
repositories/    数据库访问
models/          SQLAlchemy 模型
integrations/    外部系统适配器
workers/         异步任务
audit/           审计能力
```

Router 不得直接实现复杂业务规则、复杂 SQL 或外部调用。

## 代码要求

- 公共函数有类型注解。
- 外部调用设置超时。
- 异常转换为统一错误码。
- 事务边界由 Service 管理。
- 业务状态落数据库。
- 任务必须幂等。
- 不提交真实配置和 Secret。
