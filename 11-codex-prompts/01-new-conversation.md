# 新建对话模板

开发、测试和发布类任务的任务 ID 来源于[详细开发任务清单](../00-project/development-task-checklist.md)；普通分析任务不强制引用完整清单。

```text
你正在继续开发“银行触点载体管理系统”。

项目目录：
/Users/bianjunfeng/Desktop/linkscope1

请先读取并遵守：
1. AGENTS.md
2. docs/README.md
3. docs/00-project/project-charter.md
4. docs/00-project/master-checklist.md
5. 与本次任务相关的产品、架构、API、数据库、权限和测试文档
6. 如果本次是开发、测试或发布任务，继续读取 `docs/00-project/development-task-checklist.md`，填写对应任务 ID；普通分析任务不强制读取完整任务清单。

项目背景：
- 这是银行 NFC 触点载体管理系统，不是通用短链接后台。
- 当前业务基线为 V1.3.2 物理模型和 V3.1 模块方案。
- 正式业务模块为 M1～M5：后台访问与操作审计、组织与员工、NFC 触点资产与载体内容、触点载体员工绑定、访问事件接入与关联。
- 统计与报表是依赖 M5 和 LinkForty 只读数据的非编号横向能力；目标资源、路由规则和本地 IAM 表不建设。
- 银行后端采用 Python、FastAPI、SQLAlchemy、Alembic、PostgreSQL、Redis、Celery。
- 银行前端采用 React、TypeScript、Vite、Ant Design、TanStack Query。
- `core/` 是 LinkForty Core，负责短链接、跳转和原始访问事件。
- Casdoor 负责身份、角色和功能权限；银行后台用 `employee_code` Claim 定位员工，并按业务表范围字段执行数据过滤。
- LinkForty 写入必须通过 API，禁止直接修改平台表。
- `touchpoint_payloads` 不保存 LinkForty 专属同步状态，外部调用结果通过 `operation_logs`、`trace_id` 和任务日志追踪。
- `event_id` 是全局唯一幂等键，`click_id` 不是唯一键。
- 一期只支持 NFC，不纳入业务办理量和办理金额。

本次任务：
[填写一个具体任务]

包含范围：
[填写需要处理的模块、接口、页面、表或测试]

不包含范围：
[填写明确不允许修改的内容]

执行要求：
1. 先检查 git status 和当前实现。
2. 先报告相关文件、现状和实施方案。
3. 文档与代码不一致时，列出差异。
4. 不得把设计文档当作已实现功能。
5. 完成后执行相关测试并报告实际结果。
6. 汇报修改文件、未完成项和风险。

验收标准：
- [填写可验证的验收条件]
```
