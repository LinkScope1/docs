# V1.3.2 导出接口规范

- 只提供同步白名单字段导出，使用当前用户权限和数据范围。
- 输出格式固定为 UTF-8 CSV；不允许导出 Token、JWT、密钥、Webhook Secret 或未脱敏个人信息。
- 单次导出上限为 10 MiB 或 100,000 行，任一超限返回 `413 EXPORT_LIMIT_EXCEEDED`，不得静默截断。
- 导出操作必须写入 `operation_logs`，包含资源、范围、字段白名单、行数和结果。
- V1.3.2 不建设对象存储、下载 Token 或异步导出任务；大数据量异步导出延期到 V1.4。
- 导出失败必须记录稳定错误码；数据源不可用统一返回 `503 DATA_SOURCE_UNAVAILABLE`。

## V1.3.2 字段白名单

| 资源 | 允许字段 |
| --- | --- |
| organizations | id、orgCode、orgName、status、sortNo、locationCode、doorNo、contactName、contactPhoneMasked、description |
| employees | id、employeeCode、employeeName、orgId、phoneMasked、status、description |
| touchpoint-assets | id、assetCode、assetType、carrierUid、orgId、employeeId、assetStatus、supplierCode、supplierBatchNo、description |
| touchpoint-payloads | id、assetId、orgId、employeeId、payloadType、payloadSource、providerType、linkfortyLinkId、status、metadata |
| assignments | id、assetId、orgId、employeeId、assignmentStatus、effectiveFrom、effectiveTo、unbindReasonType、unbindReason |
| access-events | id、eventId、clickId、assetId、bindingId、orgId、employeeId、resolutionStatus、resolutionReason、receivedAt、resolvedAt |
| audit-logs | id、traceId、orgId、employeeId、operationType、objectType、objectId、operationResult、errorCode、operationTime |

手机号只导出 `phoneMasked`/`contactPhoneMasked`；不导出密文、JWT、Token、密码、Secret、原始 Payload 或完整审计详情。统计导出需要外部只读数据源可用，否则返回 503，不返回部分结果。
