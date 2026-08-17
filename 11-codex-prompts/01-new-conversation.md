# 新建对话模板

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

项目背景：
- 这是银行 NFC 触点载体管理系统，不是通用短链接后台。
- MVP 包含 M1～M8：IAM 与审计、组织与客户经理、NFC 触点载体、绑定生命周期、目标资源、路由发布、Webhook 事件、统计分析。
- 银行后端采用 Python、FastAPI、SQLAlchemy、Alembic、PostgreSQL、Redis、Celery。
- 银行前端采用 React、TypeScript、Vite、Ant Design、TanStack Query。
- `core/` 是 LinkForty Core，负责短链接、跳转和原始访问事件。
- Casdoor 负责身份、角色和功能权限；本地 IAM 负责映射和数据范围。
- LinkForty 写入必须通过 API，禁止直接修改平台表。
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
