# bank-touchpoint-platform：项目目录建设与说明

> **主版本来源**：本 Markdown 文件；[原始 DOCX](../archive/baselines/project-directory/v2.0.docx) 仅作只读归档。

> **版本**：V2.0
> **基线**：数据物理模型 V1.3.2；MVP 功能模块划分分析方案 V3.1
> **文档性质**：目标工程组织、仓库边界与协作说明
> **适用范围**：项目初始化、协作开发、跨仓库联调与目录评审
> **日期**：2026 年 8 月 19 日

> 阅读提示：本文是 V2.0 目录设计与协作边界，不把目录、接口草案、迁移或静态页面描述为已完成业务。

## 目录

1. 文档目的与基线

2. 工作区边界与状态标记

3. 最新工作区目录设计

4. 一级目录职责说明

5. M1～M5 模块对应关系

6. 模块内部结构与分层

7. 公共基础与横向能力

8. 外部系统集成目录

9. 数据库与迁移边界

10. 接口规范与文档同步

11. 根目录文件与当前实现状态

12. Git 协作与双人工作包

13. 建设顺序与开发前完成标准

14. 目录建设结论

# 1. 文档目的与基线

本文定义银行触点载体管理系统的最新工作区结构、仓库边界、业务模块落点、外部集成位置和协作规则，用于指导后续目录演进与跨仓库联调。

当前业务事实以数据物理模型 V1.3.2 为准，模块编号与研发工作包以 MVP 功能模块划分分析方案 V3.1 为准。V1.3.2 的数据结构优先于历史版本或模块文档中残留的旧表述。

- 有效业务模块为 M1～M5；旧 M1～M8 编号只用于迁移追溯，不得继续用于新需求、研发任务或验收项。

- 银行侧保留 7 张业务表：operation_logs、organization_units、employees、touchpoint_assets、touchpoint_payloads、touchpoint_employee_assignments、access_events。

- Casdoor 负责身份、角色和功能权限；LinkForty 负责链接、点击、Webhook 和访问底层能力；NFC 仅通过适配接口进入银行后台。

- 本文本身不修改 OpenAPI、数据库字典或业务代码；正式事实仍由 docs 仓库相应基线文件维护。

# 2. 工作区边界与状态标记

工作区由多个独立仓库组成，不新增一个承载全部业务代码的单体平台仓库。银行后台与 LinkForty Core 分开建设，前端只调用银行后台 API。

```text

workspace/
├── bank-touchpoint-backend/        # 【现有 / 目标】Python + FastAPI 银行后台
├── bank-touchpoint-frontend/       # 【现有 / 目标】React + TypeScript 管理后台
├── docs/                           # 【现有 / 权威】产品、架构、API、数据、安全和测试基线
├── linkforty/core/                 # 【现有 / 外部】LinkForty Core 独立服务
└── card-switch-demo/               # 【现有 / 演示】演示页面，不属于银行后台 MVP

```

| 标记 | 含义 | 文档使用规则 |
| --- | --- | --- |
| 现有 | 当前仓库可见的文件或目录 | 只说明工程骨架或边界存在，不等于业务功能已完成。 |
| 目标 | 按 V1.3.2 / V3.1 建议的最终组织方式 | 用于后续实现和评审，业务规则仍以 docs 基线为准。 |
| 迁移期 | 历史路径或兼容说明 | 可保留 README 说明，不新增旧模型、旧 API 或旧模块职责。 |
| 禁止新建 | 本版本明确下线或越界的目录/对象 | 不创建数据库表、页面菜单、API 或外部写入流程。 |

- 银行后台只写 bank_admin Schema 的业务表；LinkForty 写入必须通过 API，读取事件使用受限只读边界。

- 当前仓库可见实现仍是工程骨架、健康检查、迁移和外部边界占位；目录设计不代表 M1～M5 已完成。

# 3. 最新工作区目录设计

## 3.1 后端目标目录

```text

bank-touchpoint-backend/
├── src/app/
│   ├── api/                         # 【现有 / 目标】API 版本入口、路由注册和统一响应
│   ├── core/                        # 【现有 / 目标】配置、安全、权限基础设施、日志、Trace、审计写入、Snowflake
│   ├── db/                          # 【现有 / 目标】SQLAlchemy Base、Session、事务和数据库类型
│   ├── common/                      # 【现有 / 目标】分页、时钟、幂等和真正跨模块的纯公共类型
│   ├── modules/
│   │   ├── audit/                   # 【现有 / 目标】M1 后台访问与操作审计
│   │   ├── organizations/           # 【现有 / 目标】M2 组织与员工管理
│   │   │   └── employees/           # 【目标】M2 员工主数据子功能
│   │   ├── touchpoints/             # 【现有 / 目标】M3 NFC 资产与载体内容
│   │   ├── assignments/             # 【现有 / 目标】M4 员工绑定生命周期
│   │   ├── events/                  # 【现有 / 目标】M5 访问事件接入与关联
│   │   └── analytics/               # 【现有 / 横向】统计查询与导出，不占 M 编号、无专属表
│   ├── integrations/                # 【现有 / 目标】Casdoor、LinkForty、NFC 适配器
│   │   ├── casdoor/
│   │   ├── linkforty/
│   │   └── nfc/
│   └── workers/                     # 【现有 / 目标】Celery 异步任务、重试、补偿和对账
├── alembic/versions/                # 【现有 / 目标】银行侧 7 张表的独立 Revision
├── database/{seeds,checks}/          # 【现有 / 目标】种子、检查和辅助说明，不放正式 DDL
├── scripts/                          # 【现有 / 目标】开发、数据准备和联调辅助脚本
├── tests/                            # 【现有 / 目标】单元、API、集成、权限、幂等和迁移测试
├── docs/                             # 【现有 / 目标】后端启动、测试和联调说明
└── .github/                          # 【目标】CI、PR 模板、CODEOWNERS 和分支检查

```

## 3.2 前端目标目录

```text

bank-touchpoint-frontend/
├── src/
│   ├── app/                         # 【现有 / 目标】应用初始化、Provider 和全局错误边界
│   ├── api/                         # 【现有 / 目标】银行后台 API 封装和生成类型使用
│   ├── components/                  # 【现有 / 目标】不承载业务规则的跨页面 UI 组件
│   ├── layouts/                     # 【现有 / 目标】后台布局、导航、面包屑和权限菜单
│   ├── modules/
│   │   ├── auth/                    # 【现有 / 目标】M1 登录和访问上下文展示
│   │   ├── audit/                   # 【现有 / 目标】M1 审计查询页面
│   │   ├── organizations/           # 【现有 / 目标】M2 组织与员工页面
│   │   ├── touchpoints/             # 【现有 / 目标】M3 NFC 资产与内容页面
│   │   ├── assignments/             # 【现有 / 目标】M4 绑定、解绑和历史页面
│   │   ├── events/                  # 【现有 / 目标】M5 访问事件页面
│   │   ├── analytics/               # 【现有 / 横向】统计与导出页面，不作为 M8
│   │   └── home/                    # 【现有 / 壳层】首页和初始化工作台，不属于业务模块
│   ├── routes/                      # 【现有 / 目标】React Router 和鉴权入口
│   ├── stores/                      # 【现有 / 目标】客户端状态；服务端状态由 TanStack Query 管理
│   ├── types/                       # 【现有 / 目标】生成类型与前端公共类型组合
│   └── utils/                       # 【现有 / 目标】格式化、错误展示和纯工具函数
├── tests/                            # 【现有 / 目标】Vitest 和 Playwright
└── .github/                          # 【目标】CI、PR 模板、CODEOWNERS 和构建检查

```

## 3.3 迁移期和禁止新建目录

| 路径 | 状态 | 处理规则 |
| --- | --- | --- |
| src/app/modules/iam/ | 迁移期 | 仅保留 Casdoor/JWT 边界说明；不创建本地 iam_* 表、Repository、Service 或持久化权限投影。 |
| src/app/modules/organizations/customer_managers/ | 迁移期 | 业务对象统一使用 employees；不新增 customer_managers 表、API 或页面。 |
| src/modules/employees/ | 迁移期 | 员工能力归入前端 M2 组织与员工语义；可保留兼容说明，不单独占用模块编号。 |
| modules/resources/、src/modules/resources/ | 禁止新建 | V1.3.2 不创建 target_resources，不新增目标资源表、菜单、API 或业务流程。 |
| modules/routing/、src/modules/routing/ | 禁止新建 | V1.3.2 不创建 routing_rules，不新增路由发布、冲突或运行时规则流程。 |

# 4. 一级目录职责说明

| 目录 | 职责边界 |
| --- | --- |
| src/app/api | 注册 /api/v1 路由、解析 HTTP 参数、认证依赖、统一响应和异常映射；不得直接写 SQL 或调用外部系统。 |
| src/app/core | 提供配置、安全、权限基础设施、请求 ID、日志、Trace、公共审计写入和 Snowflake；不承载具体业务状态规则。 |
| src/app/db | 提供 SQLAlchemy Base、Session、事务和数据库类型；数据库访问由业务模块 Repository 使用。 |
| src/app/common | 只保存真正跨模块的纯公共能力，如分页、时钟、幂等和公共类型。 |
| src/app/modules | 按 M1～M5 聚合业务规则、状态解释、权限和数据访问；每张银行表只有一个责任模块。 |
| src/app/integrations | 封装 Casdoor、LinkForty API/只读/Webhook 和 NFC 适配；外部调用不得散落在 Router。 |
| src/app/workers | 承载异步任务、重试、补偿、批量导入和对账；任务结果通过 Service、Trace ID 和 M1 审计追踪。 |
| alembic | 只演进银行侧 7 张表；每次结构变化使用独立 Revision，不直接修改 LinkForty 平台表。 |
| database | 只放 seeds、checks 和辅助说明，不放正式建表逻辑。 |
| tests | 按分层和风险覆盖 API、权限、数据范围、幂等、外部失败、迁移和端到端链路。 |

## 4.1 前端目录边界

- src/api 只调用银行后台 /api/v1；前端不能直连 PostgreSQL、Redis 或 LinkForty Core。

- src/components、layouts、utils 不承载具体业务状态和权限规则；服务端返回的权限与数据范围才是最终依据。

- 每个页面必须处理 loading、empty、error 和 no permission 状态。

# 5. M1～M5 模块对应关系

| 模块 | 后端落点 | 前端落点 | 数据所有权 | 主要职责与依赖 |
| --- | --- | --- | --- | --- |
| M1 | core/security.py、integrations/casdoor、modules/audit | modules/auth、modules/audit | operation_logs | 后台访问上下文、员工定位、操作审计；依赖 Casdoor 和 M2 employees。 |
| M2 | modules/organizations/employees | modules/organizations | organization_units、employees | 组织编码层级、员工主数据、直接组织归属和数据范围根节点。 |
| M3 | modules/touchpoints | modules/touchpoints | touchpoint_assets、touchpoint_payloads | NFC 资产、卡内实际内容和 LinkForty 逻辑引用；依赖 LinkForty API、NFC。 |
| M4 | modules/assignments | modules/assignments | touchpoint_employee_assignments | 绑定、解绑、转交和历史区间；依赖 M2、M3。 |
| M5 | modules/events | modules/events | access_events | Webhook 事件幂等投影、资产/绑定/组织/员工关联和重试；依赖 LinkForty 事件或受限读取。 |

依赖链：M2 主数据 → M3 资产与内容 → M4 员工绑定 → M5 访问事件；M1 为所有管理操作、批量导入和外部调用提供横向审计上下文。

# 6. 模块内部结构与分层

业务模块按需创建固定职责文件，不批量创建空文件，也不建立全局业务型 services、repositories、models 或 schemas 目录。

```text

modules/<domain>/
├── router.py        # HTTP 协议适配和响应
├── schemas.py       # Pydantic 请求、响应和输入校验
├── service.py       # 业务规则、事务、状态变化、审计和任务调度
├── repository.py    # SQLAlchemy 查询和持久化
├── models.py        # 本模块负责的银行表模型
├── permissions.py   # 功能权限和数据范围
├── enums.py         # 状态、类型和生命周期枚举
└── exceptions.py    # 模块异常和错误码映射

Router
  → Auth / Data Scope Dependencies
  → Service
  → Domain Rules
  → Repository / Integration Adapter
  → PostgreSQL / External API

Worker / Celery Task
  → Service / Integration Adapter
  → Retry / Compensation
  → operation_logs + trace_id

```

- Service 负责组织编码、数据范围、绑定区间冲突、导入预校验、状态迁移和审计编排。

- Repository 负责 SQLAlchemy 查询、持久化、索引和数据库约束配合，不决定最终业务权限和外部平台行为。

- Integration Adapter 负责 Casdoor Claim、LinkForty API/Webhook/只读访问和 NFC 接口，需统一超时、重试、脱敏和异常。

# 7. 公共基础与横向能力

| 能力 | 目录落点 | 模块编号规则与边界 |
| --- | --- | --- |
| 身份与权限 | core/security.py、core/permissions.py、integrations/casdoor/ | Casdoor 权威；不创建本地 iam_* 表，不复制角色和功能权限。 |
| 操作审计 | core/audit.py + modules/audit/ | 写入公共化，数据所有权归 M1；operation_logs 只追加。 |
| 批量导入 | api 入口 + M3/M4 等责任模块 Service + workers/ | 横向应用能力，不占 M 编号；按责任模块预校验、更新/新增和审计。 |
| 统计与导出 | modules/analytics/ | 无编号横向只读能力；只读 access_events 和授权的 LinkForty 事件数据，不拥有本地专属表。 |
| 异步任务 | workers/ | Celery 重试、补偿、批量导入和对账；不把 Redis 当作唯一事实来源。 |
| 幂等与追踪 | common/idempotency.py、core/tracing.py | 写接口使用 Idempotency-Key；Webhook 使用全局 event_id；外部调用保留 trace_id。 |

- 统计使用 click_events.clicked_at、access_events.received_at、install_events.installed_at 和 in_app_events.event_timestamp；点击统计默认排除机器人。

- 本期不纳入银行办理量、办理金额和真实业务转化结果。

# 8. 外部系统集成目录

```text

src/app/integrations/
├── casdoor/
│   └── # JWT 验证、employee_code Claim 和外部身份边界
├── linkforty/
│   ├── client.py       # API-only 写调用
│   ├── schemas.py      # 外部对象和标准化事件类型
│   ├── webhook.py      # 验签后解析，不输出密钥
│   ├── mapping.py      # 外部字段到银行边界字段映射
│   ├── read_only.py    # 受限只读协议
│   └── exceptions.py   # 外部调用、验签和映射异常
└── nfc/
    ├── interface.py    # NFC 设备抽象
    └── mock.py         # 本地 Mock 和联调能力

```

| 集成 | 银行侧职责 | 禁止事项 |
| --- | --- | --- |
| Casdoor | 验证 JWT 签名、issuer、audience 和过期时间；读取 employee_code 定位启用员工。 | 不创建本地角色权限投影，不保存密码、Token 或身份密钥。 |
| LinkForty | M3 通过 API 执行必要外部调用；M5 通过 Webhook、受限读取或事件字段完成关联。 | 不复制 Core 源码，不直接执行外部表 DDL、DML、TRUNCATE 或迁移。 |
| NFC | M3 依赖 interface 和 Mock 先行，后续再接入经确认的硬件 SDK。 | 本期不把真实硬件写卡能力描述为已实现。 |

- Webhook 接收入口属于 M5 events；验签和字段解析属于 integrations/linkforty/webhook.py；幂等和关联属于 M5 Service。

- 禁止读取、记录或输出 Webhook 密钥值。

# 9. 数据库与迁移边界

银行后台数据库使用 PostgreSQL 14+ 的 bank_admin Schema。V1.3.2 业务库只保留 7 张银行业务表，LinkForty 的 8 张外部表不进入银行侧 Alembic 迁移。

| 责任模块 | 银行侧表 |
| --- | --- |
| M1 | operation_logs |
| M2 | organization_units、employees |
| M3 | touchpoint_assets、touchpoint_payloads |
| M4 | touchpoint_employee_assignments |
| M5 | access_events |

- 正式结构变化只能放在 alembic/versions/，每个数据库变化使用独立 Revision；database/ 只保存种子、检查和说明。

- BIGINT 雪花 ID 通过 API 以字符串传输；UUID 保留 UUID 语义；时间统一使用带时区的 TIMESTAMPTZ。

- event_id 全局唯一，click_id 仅为非唯一逻辑引用；access_events 不分区；历史绑定只追加。

- 不创建 iam_*、target_resources、routing_rules；touchpoint_payloads 不保存外部同步状态、同步时间、错误摘要或重试次数。

# 10. 接口规范与文档同步

```text

docs/03-api/openapi.yaml
          ↓  版本化同步 / 生成
bank-touchpoint-backend API 实现
          ↓
bank-touchpoint-frontend 生成 TypeScript 类型
          ↓
模块 API 封装、接口测试和跨仓库联调

```

| 规范项 | 统一约定 |
| --- | --- |
| 路径与字段 | 接口路径使用 /api/v1；JSON 使用 camelCase；数据库字段使用 snake_case。 |
| 标识与时间 | BIGINT API 返回字符串；UUID 保留 UUID；时间使用带时区 ISO 8601。 |
| 幂等 | 写接口使用 Idempotency-Key；Webhook 使用 event_id；外部写调用使用稳定幂等标识。 |
| 响应与错误 | 统一 requestId、错误码和错误结构；前端不自定义后端业务状态。 |
| 权限与范围 | 前端菜单和按钮只用于展示；后端强制校验 Casdoor 功能权限与组织/员工数据范围。 |

OpenAPI 主文件继续由 docs 仓库维护；本文件只说明目录与协作边界，不改写 openapi.yaml。

# 11. 根目录文件与当前实现状态

| 仓库/目录 | 当前可见事实 | 目录说明中的表述 |
| --- | --- | --- |
| bank-touchpoint-backend | 已有 FastAPI 工程骨架、健康检查、core/db/common、LinkForty/NFC 边界、Celery 基础和 Alembic 迁移。 | 标记为现有工程基线；M1～M5 业务闭环仍按需建设。 |
| bank-touchpoint-frontend | 已有 React 壳层、路由、组件、API 类型和 home 页面占位。 | 标记为现有管理后台骨架；业务页面不描述为已完成。 |
| docs | 拥有产品、架构、API、数据库、安全、测试、部署和运维基线。 | 作为正式规范权威来源；代码仓库不复制完整资料。 |
| linkforty/core | 独立 TypeScript/Fastify 外部系统参考项目。 | 只说明 API/只读/Webhook 边界，不复制源码或直接操作平台表。 |
| card-switch-demo | 演示页面工程。 | 只作为演示或实验目录，不作为完整银行后台实现。 |

## 11.1 根目录最低约定

- 两个业务仓库各自维护 AGENTS.md、README.md、环境示例、依赖锁定、测试配置和 .github CI；不共享一套业务代码目录。

- 环境变量不得提交真实密码、Token、Webhook Secret、数据库密码或生产配置；.env 必须被 .gitignore 忽略。

- README 必须说明启动、测试、迁移、类型生成和联调命令；文件存在只代表工程约定，不代表功能完成。

# 12. Git 协作与双人工作包

```text

main
├── feature/M1-access-audit
├── feature/M2-organizations-employees
├── feature/M3-touchpoints
├── feature/M4-assignments
└── feature/M5-access-events

```

| 工作包 | 负责模块 | 主要数据表 | 交接内容 |
| --- | --- | --- | --- |
| A | M1～M3 | operation_logs、organization_units、employees、touchpoint_assets、touchpoint_payloads | 访问上下文、审计、组织员工主数据、NFC 资产和 Payload；向 B 提供组织/员工/资产/Payload 校验、外部 Link 引用和审计上下文。 |
| B | M4～M5 | touchpoint_employee_assignments、access_events | 绑定、解绑、调拨、事件幂等、资产关联和访问事件查询；向 A 的审计能力写入绑定及事件处理结果。 |

- main 禁止直接提交；每个 PR 聚焦一个业务模块或一个公共变更；API、迁移、权限、幂等和公共代码必须双人审核。

- 两个业务仓库分别进行版本和发布管理，统一从 `main` 创建短期分支，不维护长期集成分支。

# 13. 建设顺序与开发前完成标准

| 阶段 | 工作包 A | 工作包 B | 共同验收 |
| --- | --- | --- | --- |
| 第一阶段 | M1～M3 基础能力、主数据和触点资产 | 准备 M4～M5 接口和依赖 | 身份、范围、资产、Payload 和审计字段契约。 |
| 第二阶段 | 提供稳定的组织、员工、资产和 Payload 基础 | M4～M5 绑定生命周期、事件幂等与关联 | 资产—绑定—事件关联链路。 |
| 第三阶段 | 共同补齐权限、审计和边界检查 | 共同补齐外部失败、重试和补偿 | 跨模块权限、幂等、补偿和文档验收。 |

- FastAPI、React、PostgreSQL、Redis、Celery、Alembic 和 CI 均可启动并通过基础检查。

- Casdoor JWT、employee_code Claim、LinkForty 网络访问边界、Webhook 验签要求和 NFC Mock 均有明确的验证范围；LinkForty 正式路径、字段、错误、幂等契约和真实 Webhook 样例仍待外部确认。

- 7 张银行业务表可在空数据库完成迁移，权限、数据范围、事件幂等、外部失败补偿和审计测试已准备。

- M1～M5 目录职责、API 第一批契约、OpenAPI 同步方式和两个工作包的交接字段已确认。

- 任何“已实现”结论必须提供代码路径、类/函数、接口、迁移或测试证据；目录存在不作为实现证据。

# 14. 目录建设结论

- 继续使用两个独立业务仓库承载银行后台和管理后台，不新增单体平台代码仓库。

- 后端采用 src/app + 业务模块化单体；前端采用 React 模块化页面结构；M1～M5 是唯一有效业务模块编号。

- docs 继续作为正式需求、架构、API、数据库、安全和测试基线；本文件是 V2.0 目录说明的 Markdown 主版本来源。

- LinkForty Core 保持独立，card-switch-demo 仅作为演示；银行后台通过 Integration Adapter 和受限只读边界交互。

- analytics、批量导入、Worker、NFC Adapter 和操作审计是横向或外部能力，不提前占用新的业务模块编号。

- 后续目录变化必须同步更新本说明，并明确涉及的业务边界、数据所有权、权限、API、迁移和测试影响。
