# 认证方案

## Casdoor

Casdoor 负责身份、角色和功能权限。银行后台负责 JWT 验证、员工定位和业务数据范围校验。

## 验证步骤

1. 获取并缓存 JWKS。
2. 验证 JWT 签名。
3. 验证 issuer。
4. 验证 audience。
5. 验证 subject、过期时间和时钟偏差。
6. 读取稳定的 `employee_code` Claim。
7. 用 `employee_code` 查询 `bank_admin.employees`。
8. 检查员工状态是否启用。
9. 构建员工、组织和数据范围上下文。

## 数据范围

- Casdoor 角色决定功能权限。
- `employees.org_id` 决定员工直接组织归属。
- 业务表按 `org_id`、`employee_id` 执行后端过滤。
- 前端传入的员工 ID 或组织 ID 不能改变认证主体和数据范围。

## 禁止

- 本地保存密码、Token 或密码哈希。
- 创建 `iam_*` 表作为身份、角色或权限来源。
- 使用前端按钮代替后端权限校验。
- 使用请求参数中的用户或员工 ID 代替 JWT 主体。

## 外部契约待验证

Casdoor 必须确认 `employee_code` Claim 的名称、格式、稳定性和停用同步策略；在契约确认前不得宣称认证链路已完成。
