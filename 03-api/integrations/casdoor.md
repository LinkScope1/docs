# Casdoor 集成契约

## 状态

银行后台物理模型 V1.3.2 约定使用 Token 中的 `employee_code` Claim 定位员工；issuer、audience、JWKS 和 Claim 实际格式仍需外部平台确认。

## 必须确认

- issuer
- audience
- JWKS URI
- `employee_code` Claim 名称、类型和稳定性
- 角色和权限编码
- 员工停用同步方式
- JWKS 轮换策略
- 时钟偏差容忍范围

## 后端行为

1. 获取并缓存 JWKS。
2. 未知 `kid` 触发 JWKS 刷新；缓存只保存公钥，不保存私钥。
3. 校验 JWT 签名、issuer、audience、subject 和过期时间；默认时钟偏差为 60 秒。
4. 读取非空字符串 `employee_code`。
5. 每次请求查询 `employees.employee_code`，不存在、停用、Claim 缺失或类型错误均拒绝访问。
6. 使用 Casdoor 功能角色和银行业务表范围字段完成授权；不把角色复制到本地 IAM。

## 禁止

- 保存密码或 Token。
- 使用本地 IAM 表复制 Casdoor 权威数据。
- 用前端菜单代替后端权限。
