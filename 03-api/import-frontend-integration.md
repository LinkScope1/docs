# 导入流程与失败处理：前端接入说明

> 面向银行后台前端开发。本文说明导入预校验、执行结果展示、失败报告下载和批次轮询。API 字段的唯一契约以 [`openapi.yaml`](./openapi.yaml) 为准；模板表头和业务字段规则以 [`import-templates.md`](./import-templates.md) 为准。

## 1. 推荐接口流程

新接入优先使用统一导入流程：

```text
下载模板 / 选择文件
        ↓
POST /api/v1/imports/validate
        ↓
展示预校验结果；修正文件后重新校验
        ↓
POST /api/v1/imports/execute（携带 Idempotency-Key）
        ├─ 200：同步执行完成，检查 completion、failures 和 failureReport
        └─ 202：批次已入队，轮询 GET /api/v1/imports/{batchId}
                    ↓ completed
             GET /api/v1/imports/{batchId}/failure-report
```

统一执行接口在 1,000 行以内同步执行，超过 1,000 行返回 `202` 并由后台任务执行；单文件上限为 10 MiB、100,000 条数据行。每行独立处理，因此部分行失败不会撤销其他成功行。

目前还存在员工专用接口 `POST /api/v1/imports/employees/execute`：它同步处理最多 1,000 行，不使用 `Idempotency-Key`，失败报告直接随响应返回。该接口和统一接口的返回及重试行为不同；新功能不要在同一页面中混用两套执行接口。若现有页面仍使用员工专用接口，应按第 4 节处理其响应。

## 2. 预校验结果

调用 `POST /api/v1/imports/validate`，使用 `multipart/form-data` 传入：

- `file`：待导入 CSV；地址页面也支持下载的 XLSX 模板。
- `templateType`：`asset`、`payload`、`employee` 或 `address_page`。

行级问题在成功响应的 `data.rows[].errors[]` 中，包含行号、字段和错误类型。预校验是只读操作，不写业务表。若 `data.invalid > 0`，建议默认展示错误行并要求用户修正后重新校验；若产品允许继续执行部分有效行，必须在界面上明确提示“执行可能产生部分成功”，并让用户确认。

预校验响应不包含 `failureReport`。文件无法解析、表头不合法等整文件错误通过 HTTP 错误响应返回，前端应展示全局错误，不要尝试读取失败报告。

## 3. 执行响应与界面行为

### 同步完成：HTTP 200

统一接口响应的 `data` 包含：

- `batchId`、`status`、`total`、`succeeded`、`failed`；
- `rows[]`：逐行 `rowNumber`、`status`、`operation`，以及失败时的 `errorCode`、`message`；
- `failureReport`：有失败行时为报告对象，无失败行时为 `null`。

`status: "completed"` 表示处理流程结束，不表示所有行都成功。是否有部分失败应依据 `failed` 判断。执行结束后展示 `completion.message`、成功数、失败数；当 `failed > 0` 时，直接使用 `failures` 显示失败行摘要，并显示“下载失败报告”按钮。后端不负责操作浏览器弹窗，但响应已经提供前端弹窗所需的完成状态和文案。

### 异步入队：HTTP 202

初始响应提供 `batchId`、`status: "queued"` 和 `completion.outcome: "processing"`。此时尚无最终逐行结果，不要显示为导入成功，也不要尝试下载失败报告。使用 `GET /api/v1/imports/{batchId}` 轮询状态：

| 批次状态 | 前端处理 |
|---|---|
| `queued` / `running` | 显示处理中；继续轮询 |
| `completed` 且 `failed = 0` | 显示全部成功 |
| `completed` 且 `failed > 0` | 展示 `completion.message`、成功/失败数量及 `failures`；显示失败报告下载按钮 |
| `failed` | 展示 `error.message`、`error.errorCode` 和 `error.stage`，并保留 `batchId` / `requestId` 供排查；不要假设一定有失败 CSV |

建议轮询采用有间隔并逐步退避的策略，在页面离开、用户取消或达到合理超时时停止；不要高频连续请求。

## 4. 失败报告下载

### 执行响应内的报告：Base64

统一接口同步响应和员工专用接口的 `data.failureReport` 结构为：

```json
{
  "filename": "员工导入失败报告.csv",
  "contentType": "text/csv;charset=utf-8",
  "encoding": "base64",
  "content": "..."
}
```

仅当存在失败行时才有报告对象。前端应将 `content` 从 Base64 解码为字节后，以 `contentType` 创建 Blob，并使用服务端返回的 `filename` 下载。报告为 UTF-8 BOM CSV；不要把 Base64 字符串直接保存为 CSV 文本。

### 异步批次报告：直接 CSV

批次完成且有逐行失败时，调用：

```http
GET /api/v1/imports/{batchId}/failure-report
```

成功响应是 `text/csv` 文件流，浏览器端直接读取 Blob 下载，不做 Base64 解码。若没有报告（例如批次没有逐行失败，或发生整批级技术失败），接口会返回 `404`；先读取批次状态和 `failures` 再决定是否调用。

访问批次和下载报告要求 `import.validate` 权限；非全局用户只能访问自己创建的批次。前端遇到 `403` / `404` 应展示访问或资源提示，不要无限重试。

## 5. 错误分类和提示

| 情况 | 识别方式 | 建议处理 |
|---|---|---|
| 行级业务错误 | 校验响应的 `invalid` / `rows[].errors`，或执行响应的 `failed` / `rows[].errorCode` | 展示行号、字段、原因；执行后可下载失败报告 |
| 文件或模板错误 | HTTP `400`、`413`、`415`、`422` | 显示接口 `message`；提示检查表头、文件类型、大小或请求字段 |
| 幂等键冲突 | HTTP `409`，`IDEMPOTENCY_CONFLICT` | 不要自动换文件重试同一请求；提示重新确认文件并为新的逻辑导入生成新键 |
| 任务入队或数据源不可用 | HTTP `503` | 提示稍后重试；保留 `requestId` 供排查 |
| 批次执行级失败 | 查询结果 `status: "failed"` | 显示通用失败提示和 `batchId` / `requestId`；若没有报告，不要反复请求报告接口 |

对同一个文件和模板的网络重试应复用同一个 `Idempotency-Key`；用户选择了新文件或新模板后应生成新的键。不要因前端超时就无条件重新提交并创建另一批导入。

## 6. 隐私与日志

- 失败 CSV 的员工联系方式为脱敏值；不得在浏览器控制台、前端埋点或错误上报中记录原始手机号、完整导入文件或 Base64 报告内容。
- 失败报告中可能包含姓名、工号、组织编码等定位字段；仅在有权限的管理页面提供下载，不应写入通用日志。
- 页面或客服排查优先保留 `requestId` 和 `batchId`。审计记录位于后端操作日志，前端不直接访问数据库或审计表。

## 7. 当前接口边界与需后端确认项

1. **批次级失败已提供结构化原因。** `GET /imports/{batchId}` 在 `status: "failed"` 时返回 `error.stage`、`error.errorCode` 和安全的 `error.message`；整批技术失败可能没有 `failureReport`，前端应直接在完成窗口显示该错误对象。
2. **员工有两条执行路由。** 新前端默认按本项目导入规范使用统一执行接口；若决定继续用员工专用路由，应在需求/API 契约中明确其 1,000 行同步上限及无幂等批次查询的差异。
3. **预校验错误仍不生成后端失败文件。** 预校验响应新增 `completion`，逐行错误仍由 `data.rows[].errors[]` 返回。若页面需要“下载预校验错误清单”，由前端基于响应生成；不可假设预校验会生成 `failureReport`。

## 8. 验收清单

- [ ] 校验失败时能展示逐行错误，不把行级失败误当成 HTTP 请求失败。
- [ ] 执行完成后按 `failed` 显示全成功或部分成功；不会仅依据顶层 `status` 判断。
- [ ] 完成窗口使用 `completion.message` 和统计字段；行级失败直接使用 `failures`，批次级失败直接使用 `error`。
- [ ] 同步 Base64 报告能正确解码并按返回文件名下载。
- [ ] 异步流程能处理 `202`、轮询批次，并直接下载 CSV 响应。
- [ ] 批次级失败无报告时展示通用提示和关联 ID，不无限重试。
- [ ] 新文件使用新 `Idempotency-Key`，同请求重试复用原键。
- [ ] 前端日志、埋点和错误上报不包含手机号、导入原文或报告内容。
