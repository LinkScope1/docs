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
src/app/
├── api/                       全局路由注册、健康检查等 HTTP 入口
├── core/                      配置、错误处理、Request ID 和访问上下文
├── common/                    跨模块复用的响应、分页和公共类型
├── db/                        Session、Base 和统一 ORM 模型注册
├── modules/                   M1–M5 业务模块
│   └── <domain>/              模块内的 Router、Schema、Service、Repository 和 ORM
├── integrations/             Casdoor、LinkForty、NFC 等外部系统适配器
└── workers/                  Celery 异步任务、重试、补偿和对账
```

业务代码优先按领域放入 `modules/<domain>/`，不得再建立与 `modules/` 平行的全局 `services/`、`repositories/` 或 `models/` 目录。跨模块公共能力只有在确实被多个模块复用时才放入 `common/`、`core/` 或 `db/`。

Router 不得直接实现复杂业务规则、复杂 SQL 或外部调用。

## 代码要求

- 公共函数有类型注解。
- 外部调用设置超时。
- 异常转换为统一错误码。
- 事务边界由 Service 管理。
- 业务状态落数据库。
- 任务必须幂等。
- 不提交真实配置和 Secret。
