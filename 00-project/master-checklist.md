# 项目总工作清单

## P0：开发前必须完成

- [ ] 确认银行后台与 LinkForty Core 边界
- [x] 确认 Python 后端和前端真实代码目录：`bank-touchpoint-backend/`、`bank-touchpoint-frontend/`；当前仅为工程骨架
- [ ] 确认 MVP 范围和不纳入项
- [ ] 确认 M1～M5 负责人以及工作包 A、B 的主负责人
- [ ] 完成 Casdoor PoC，并确认 `employee_code` Claim
- [ ] 完成 LinkForty API PoC
- [ ] 获取并验证真实 Webhook 样例
- [ ] 确认 NFC/NDEF 设备或 Mock 方案
- [ ] 确认 PostgreSQL、Redis 和环境访问权限
- [ ] 确认数据库角色和 LinkForty 只读权限
- [ ] 冻结 V1.3.2 物理模型、V3.1 模块方案、权限矩阵、API 规范、7 张表数据字典和状态机
- [ ] 配置 Git 分支保护、PR 模板和 CI 基础检查

## P1：第一轮开发前完成

- [ ] FastAPI 工程可启动
- [ ] React 工程可启动
- [ ] PostgreSQL 可连接
- [ ] Redis 和 Worker 可启动
- [ ] Alembic 初始迁移可执行
- [ ] Casdoor JWT 可验证
- [ ] 测试用户、角色和组织已准备
- [ ] 第一条垂直业务切片已确定

## P2：开发中持续完成

- [ ] 工作包 A：M1/M2/M4 审计、组织员工和绑定生命周期闭环
- [ ] 工作包 B：M3/M5 资产内容、LinkForty 集成和访问事件闭环
- [ ] 非编号统计与报表能力完成 M5 和 LinkForty 只读数据联调
- [ ] 每个正式模块和横向能力同步更新 API、数据、测试和验收资料
- [ ] 每个 PR 完成代码审核和 CI
- [ ] 每个阶段完成演示和阶段验收

## P3：上线前完成

- [ ] 权限和越权测试通过
- [ ] Webhook 幂等和重放测试通过
- [ ] 外部失败补偿验证通过
- [ ] 数据迁移和数据质量检查通过
- [ ] 备份恢复演练通过
- [ ] 回滚演练通过
- [ ] 监控和告警生效
- [ ] 生产配置审核完成
- [ ] MVP 验收矩阵关闭

## 当前待确认项

| 事项 | 负责人 | 截止时间 | 状态 |
|---|---|---|---|
| 银行后台 Python/React 工程目录及实现状态 | 待指定 | 2026-08-19 | 已确认目录；业务闭环待开发 |
| Casdoor issuer/audience/JWKS/employee_code Claim | 平台/安全 | 待指定 | 待确认 |
| LinkForty API 契约 | LinkForty 负责人 | 待指定 | 待确认 |
| Webhook 签名和事件样例 | LinkForty 负责人 | 待指定 | 待确认 |
| NFC 设备和 NDEF 方案 | 硬件/业务 | 待指定 | 待确认 |
| 数据库部署和只读账号 | 数据库/运维 | 待指定 | 待确认 |
