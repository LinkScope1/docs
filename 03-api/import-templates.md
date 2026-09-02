# V1.3.2 导入模板

本文档是银行后台三类 CSV 导入模板的列和版本说明。导入在 V1.3.2 只提供同步预校验，接口为 `POST /api/v1/imports/validate`；系统不会在预校验期间写入业务表，也不提供 `/api/v1/imports/execute`。

## 1. 版本与通用规则

- 三类模板的 Schema 版本均为字符串 `"1"`。这是模板格式版本，不是产品版本。
- V1.3.2 不新增 `templateVersion` 请求字段，也不要求 CSV 文件包含版本列。没有版本字段的历史 CSV 仍可进行预校验。
- CSV 字段使用 camelCase；数据库和业务术语在本文说明中使用 snake_case。
- 文件使用 UTF-8 编码，UTF-8 BOM 也兼容。空白值按空值处理。
- 未知列、重复列、缺少必要列和不支持的模板类型会被拒绝；逐行错误包含行号、字段和错误类型，但不回显原始 CSV 值。
- 缺少某一行不代表删除、停用或解绑。解绑或替换意图必须由显式 `operation` 表达。
- 预校验结果只用于提示预计新增、更新、跳过和逐行错误；异步执行、任务状态、结果持久化和批量业务写入属于后续版本。

文件预校验规则：

- 导入文件只支持 CSV。文件名存在时必须以大小写不敏感的 `.csv` 结尾；文件名缺失或为空时继续按 CSV 内容校验。
- Content-Type 为空时继续按 CSV 内容校验；明确提供时允许 `text/csv`、`application/csv`、`text/plain` 和 `application/vnd.ms-excel`，可带 MIME 参数。其他类型返回 `415 IMPORT_FILE_TYPE_INVALID`。
- 文件大小不得超过 10 MiB，数据行不得超过 100,000 行；超过限制返回 `413 IMPORT_FILE_TOO_LARGE`。正好达到限制时允许继续校验。
- 文件必须使用 UTF-8 或 UTF-8 BOM 编码；非法编码返回 `400 IMPORT_ENCODING_INVALID`。CSV 语法错误或数据行列数异常返回 `400 IMPORT_CSV_INVALID`。
- 表头必须符合对应模板元数据定义。缺失列、未知列、重复列或顺序错误返回 `400 IMPORT_COLUMNS_INVALID`；空白必填值按空值处理。
- 错误响应只返回必要的行号、字段名和错误类型，不回显原始 CSV 内容、Payload 值、手机号或凭证。
- V1.3.2 仍只提供 `POST /api/v1/imports/validate`，不提供 `POST /api/v1/imports/execute`。

## 2. 载体内容模板 `payload`

用途：预校验载体实际写入的内容，并通过载体业务编码或 NFC 物理 UID 定位资产。

规范表头及顺序：

```csv
payloadType,payloadValue,payloadSource,assetCode,carrierUid
```

| 列 | 要求 | 含义 |
|---|---|---|
| `payloadType` | 必填 | 载体内容类型编码 |
| `payloadValue` | 必填 | 卡内实际写入内容；示例使用脱敏固定值 |
| `payloadSource` | 必填 | 内容来源编码 |
| `assetCode` | 条件必填 | 载体业务编码，精确匹配 `asset_code` |
| `carrierUid` | 条件必填 | NFC 物理 UID，精确匹配 `carrier_uid` |

每行至少提供 `assetCode` 或 `carrierUid` 一个。两者同时提供时，必须精确解析到同一个资产；如果一个已匹配而另一个匹配到其他资产或无法证明一致，整行报错，不能静默选择其中一个。两者均未匹配时，预校验可将该行标记为预计新增，但不会实际创建资产或内容。

`assetCode` 是银行业务编码，适合业务查询和导入；`carrierUid` 是 NFC 实体的物理 UID，适合盘点。两者不能互相替代。

历史文件可以省略 `assetCode` 或 `carrierUid` 的其中一列，但每行仍至少提供一个资产标识；文件不需要增加 `templateVersion` 列。

脱敏示例：

```csv
payloadType,payloadValue,payloadSource,assetCode,carrierUid
1,https://example.invalid/demo,2,TP-DEMO-001,NFC-DEMO-001
```

## 3. 载体员工绑定模板 `assignment`

用途：预校验载体与员工绑定生命周期操作。

规范表头及顺序：

```csv
assetCode,employeeCode,operation
```

| 列 | 要求 | 含义 |
|---|---|---|
| `assetCode` | 必填 | 载体稳定业务编码，精确匹配 `asset_code` |
| `employeeCode` | 必填 | 员工稳定业务编码，精确匹配 `employee_code` |
| `operation` | 必填 | 绑定操作类型 |

`operation` 仅支持以下值：

- `bind`：表达显式绑定意图。
- `unbind`：表达显式解绑意图。
- `transfer`：表达显式转交意图；跨组织转交仍需满足独立权限和数据范围规则。

绑定模板不使用员工姓名或载体名称模糊匹配。示例：

```csv
assetCode,employeeCode,operation
TP-DEMO-001,EMP-DEMO-001,bind
TP-DEMO-002,EMP-DEMO-002,unbind
TP-DEMO-003,EMP-DEMO-003,transfer
```

## 4. 载体内容关系模板 `asset_payload_relation`

用途：预校验资产与载体内容之间的关系描述。

规范表头及顺序：

```csv
assetCode,payloadValue,payloadType,payloadSource
```

四列均为必填：

| 列 | 含义 |
|---|---|
| `assetCode` | 载体稳定业务编码，精确匹配 `asset_code` |
| `payloadValue` | 载体内容值 |
| `payloadType` | 载体内容类型编码 |
| `payloadSource` | 内容来源编码 |

当前模板层面的稳定关系描述为 `assetCode + payloadType + payloadValue`。不使用 `carrierUid` 代替 `assetCode`，也不使用载体或内容名称模糊匹配。示例：

```csv
assetCode,payloadValue,payloadType,payloadSource
TP-DEMO-001,https://example.invalid/demo,1,2
```

## 5. 组织和敏感数据边界

- `org_code` 是组织稳定业务键，用于后端数据权限和资产责任组织范围校验；V1.3.2 不新增 `orgCode` CSV 列。
- `employee_code` 是员工稳定业务键，不等同于姓名、手机号或 Casdoor 内部标识。
- 示例中的资产编码、UID、员工编码和内容均为脱敏固定值，不代表真实业务数据。
- CSV 内容、Token、JWT、Webhook Secret、数据库密码和未脱敏个人信息不得写入日志、错误消息、文档示例或测试输出。
