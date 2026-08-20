# 前端开发规范

## 技术

- React + TypeScript + Vite。
- React Router 管理路由。
- TanStack Query 管理服务端状态。
- OpenAPI 生成 API 类型。
- Ant Design 作为基础组件库。

## 规则

- 页面、组件、请求和类型分离。
- 前端与后台交互固定采用“统一 API Client + 领域 Service + TanStack Query Hooks”三层结构。
- `src/api/client.ts` 只负责请求传输、认证头、超时、`requestId`、统一响应 Envelope 和错误转换。
- `src/api/services/` 按 M1～M5 和横向能力封装领域 API；每个 Service 方法只表达一个明确的领域操作。
- `src/api/hooks/` 负责 Query、Mutation、缓存键、失效和刷新策略。
- 页面和组件只能调用领域 Service 或 Hooks，不得直接调用 `fetch`、`axios` 或拼装后台 URL。
- 不重复手写后端接口类型。
- OpenAPI 生成类型是后台接口类型的唯一来源；API 类型变化必须先更新 OpenAPI 并重新生成。
- 列表页面统一分页、筛选、排序和空状态。
- 危险操作必须二次确认。
- 权限不足必须展示明确提示。
- 前端权限只用于展示，后端权限才是最终依据。
- 所有导出显示当前数据范围。

## 统一通信和公共 JS 交互

- Client 统一处理 401、403、409、422、500、网络超时、`requestId`、错误码和用户可读错误信息。
- Query/Mutation 统一处理请求状态、重复提交控制和成功后的 Query 缓存失效；页面不得自行复制这些逻辑。
- 领域幂等、Webhook `event_id`、稳定业务键和外部 LinkForty 幂等标识必须遵循后台 API 契约。
- 通用 `Idempotency-Key` 在 `DEC-IDEMP-001` 完成前不得由前端自行决定持久化方式。
- 公共错误提示、成功提示、确认操作、提交锁定、分页、筛选、排序、加载、空数据、错误和无权限状态必须沉淀为公共 Hook、工具函数或组件。
- 公共 JS 和组件不得包含具体业务权限规则、业务接口 URL 或未脱敏的敏感数据。
- 日志、错误提示和前端状态不得暴露 Token、密码、Webhook Secret 或内部堆栈。
