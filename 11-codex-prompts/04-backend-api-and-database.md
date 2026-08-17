# Python 后端、API 和数据库开发模板

```text
请实现或审查以下 Python 后端功能：

功能：
[填写]

请检查并按项目规范处理：
- FastAPI Router
- Pydantic Request/Response Schema
- Service 业务规则
- Repository 数据访问
- SQLAlchemy Model
- Alembic Migration
- 事务边界
- 唯一约束和索引
- API 错误码和状态码
- 权限和组织数据范围
- 幂等键
- 审计日志
- 单元测试、Service 测试、Repository 测试和 API 集成测试

架构要求：
- Router -> Service -> Repository
- 外部系统调用使用 Integration Adapter
- 业务规则不得散落在 Router 或前端
- 外部调用不能与数据库事务假设为同一个原子事务
- BIGINT API 字段使用字符串
- `event_id` 全局唯一，`click_id` 非唯一

请输出：
1. 当前实现和代码证据
2. 实施方案
3. 接口和数据变更
4. 事务、幂等和失败处理
5. 修改内容
6. 测试结果和剩余风险
```
