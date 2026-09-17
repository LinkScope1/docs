# CSV 导出规范

导出是横向能力，组织不作为可导出资源。接口为 `GET /api/v1/exports/{resource}`，结果始终是“当前用户数据范围 ∩ 查询筛选条件”，筛选只能收窄范围。CSV 使用 UTF-8 BOM，最多 100,000 行、10 MiB；超限返回 `413 EXPORT_LIMIT_EXCEEDED`，不得静默截断。成功和失败均写入 M1 操作审计。

成功响应仍为 CSV 文件流，并额外返回以下 ASCII 响应头。前端读取这些响应头后即可展示完成窗口，不需要改变现有 Blob 下载逻辑：

| 响应头 | 示例 | 含义 |
| --- | --- | --- |
| `X-Export-Status` | `completed` | 导出流程已完成 |
| `X-Export-Outcome` | `success` | 本次导出结果 |
| `X-Export-Message-Code` | `EXPORT_COMPLETED` | 稳定提示码 |
| `X-Export-Total` | `125` | CSV 数据行数 |
| `X-Export-Succeeded` | `125` | 成功导出行数 |
| `X-Export-Failed` | `0` | 导出失败行数；当前同步导出成功时固定为 0 |

后端通过 CORS `Access-Control-Expose-Headers` 暴露上述响应头。导出失败时不返回伪造的 CSV，继续使用统一 JSON 错误结构中的 `requestId`、`error.code` 和 `error.message`，前端应在窗口中显示错误。

## 支持资源与表头

| 资源 | 固定表头 |
| --- | --- |
| 员工 | 员工编号、员工ID、姓名、组织编码、脱敏手机号、状态、备注 |
| 卡片 | 卡ID、物理UID、责任组织编码、状态、供应商编码、供应商批次、绑定员工编号、绑定员工姓名、绑定地址编码、绑定地址标识、LinkForty短链接、备注 |
| 载体内容 | 内容ID、内容类型、内容来源、提供方、内容状态、卡ID、物理UID |
| 地址页面 | 地址ID、地址编码、地址标识、URL、内容类型、目标地址、组织编码、状态、APP iOS Scheme、APP Android Scheme、APP Harmony Scheme、APP Payload、APP回退地址、说明 |

另支持绑定历史、访问事件、操作审计等受控资源；其字段以 API 白名单为准。普通导出不提供组织资源。

## 资产导出与 LinkForty 短链

卡片导出会带出当前绑定员工、当前有效 Payload 关联的地址页面，以及本地已落库的 LinkForty 短链接快照。没有有效绑定、页面或短链快照时对应单元格为空；导出过程不现场调用 LinkForty，也不从外部平台表读取数据。

资产筛选支持 `cardId`、`carrierUid`、`orgCode`、`employeeId`、`employeeName`、`assetStatus`、`supplierBatchNo`、`assetIds`、`createdFrom`、`createdTo`。`cardId` 按卡ID前缀匹配；`assetIds` 是逗号分隔的正数 BIGINT 字符串内部主键，日期必须带时区。

## 地址页面导出

地址页面导出保留 APP/网页/小程序统一字段。APP 行的“目标地址”列输出为空，`APP回退地址` 从 APP 元数据中输出；平台 Scheme 与 APP Payload 原样输出。网页/小程序的 APP 专用字段为空。需要回填导入时按业务字段映射到地址页面统一模板；导出的地址 ID、状态和目标地址不是导入模板列，不能直接作为导入列上传。地址编码只允许更新已有页面，不能覆盖责任组织。

## 载体内容原值

普通载体内容导出不包含原始“内容值”。只有 `mode=content` 且调用者具备 `export.payload-content` 权限时才增加“内容值”列；后端仍会二次校验权限，前端必须二次确认。手机号只输出脱敏值，不输出密文、完整手机号、Token、密码、Webhook Secret 或数据库凭证。
