# V1.3.2 导入模板

本文档是银行后台三类 CSV 导入模板的列和版本说明。导入在 V1.3.2 只提供同步预校验，接口为 `POST /api/v1/imports/validate`；系统不会在预校验期间写入业务表，也不提供 `/api/v1/imports/execute`。

## 1. 版本与通用规则

- 三类模板的 Schema 版本均为字符串 `"1"`。这是模板格式版本，不是产品版本。
- V1.3.2 不新增 `templateVersion` 请求字段，也不要求 CSV 文件包含版本列。没有版本字段的历史 CSV 仍可进行预校验。
- CSV 字段使用 camelCase；数据库和业务术语在本文说明中使用 snake_case。
- 文件使用 UTF-8 编码，UTF-8 BOM 也兼容。空白值按空值处理。
- 未知列、重复列、缺少必要列和不支持的模板类型会被拒绝；逐行错误包含行号、字段和错误类型，但不回显原始 CSV 值。
- 缺少某一行不代表删除、停用或解绑。绑定模板中的解绑或转交意图必须由显式 `operation` 表达。
- 预校验结果只用于提示预计新增、更新、跳过和逐行错误；异步执行、任务状态、结果持久化和批量业务写入属于后续版本。

文件预校验规则：

- 导入文件只支持 CSV。文件名存在时必须以大小写不敏感的 `.csv` 结尾；文件名缺失或为空时继续按 CSV 内容校验。
- Content-Type 为空时继续按 CSV 内容校验；明确提供时允许 `text/csv`、`application/csv`、`text/plain` 和 `application/vnd.ms-excel`，可带 MIME 参数。其他类型返回 `415 IMPORT_FILE_TYPE_INVALID`。
- 文件大小不得超过 10 MiB，数据行不得超过 100,000 行；超过限制返回 `413 IMPORT_FILE_TOO_LARGE`。正好达到限制时允许继续校验。
- 文件必须使用 UTF-8 或 UTF-8 BOM 编码；非法编码返回 `400 IMPORT_ENCODING_INVALID`。CSV 语法错误或数据行列数异常返回 `400 IMPORT_CSV_INVALID`。
- 每个数据行的字段数必须与表头一致；多余或缺少字段均返回 `400 IMPORT_CSV_INVALID`，错误详情仅包含该行 `rowNumber`、`field=columns` 和 `type=invalid`，且不会进入数据库查询。
- 表头必须符合对应模板元数据定义。缺失列、未知列、重复列或顺序错误返回 `400 IMPORT_COLUMNS_INVALID`；空白必填值按空值处理。
- 错误响应只返回必要的行号、字段名和错误类型，不回显原始 CSV 内容、Payload 值、手机号或凭证。
- V1.3.2 仍只提供 `POST /api/v1/imports/validate`，不提供 `POST /api/v1/imports/execute`；预校验不执行任何业务状态变化。

### 显式行操作和缺失行安全规则

- 只有 `assignment` 模板包含必填的 `operation` 列；`payload` 和 `asset_payload_relation` 不接受操作列。
- `assignment.operation` 仅支持 `bind`、`unbind`、`transfer`。`delete`、`disable`、`replace`、空值和其他值均返回该行的 `unsupported` 或 `required` 错误。
- `bind` 表达显式绑定意图，`unbind` 表达显式解绑意图，`transfer` 表达显式转交意图；转交仍受 M4 的权限和数据范围规则约束。
- CSV 未出现的既有资产、内容或绑定不会参与差异计算，不会被推导为删除、停用、解绑或其他状态变化。需要改变绑定关系时，必须在对应 CSV 行明确填写 `unbind` 或 `transfer`。
- 导入预校验只对文件中实际存在的行返回 `create`、`update`、`skip` 或逐行错误；V1.3.2 不写入业务表。

### 稳定键和精确匹配

- 解析每个单元格时只去除首尾空白；业务键大小写敏感，不做大小写折叠、`LIKE` 或其他模糊匹配。
- `payload` 的稳定键优先使用 `assetCode`，没有时使用 `carrierUid`；`assignment` 使用 `assetCode + employeeCode`；`asset_payload_relation` 使用 `assetCode + payloadType + SHA-256(payloadValue)`。关系模板的 `payloadSource` 不是稳定键的一部分。
- 资产按 `asset_code` 或 `carrier_uid` 精确查询，员工按 `employee_code` 精确查询，关系按 `asset_id + payload_type + payload_value` 精确查询。关系稳定键和返回的 `stableKey` 只包含 `payloadValue` 的 SHA-256 摘要，不返回原始内容。
- 同一文件中的稳定键只保留第一行；后续行返回 `duplicate_in_file`，错误包含该行 `rowNumber` 和稳定键字段。数据库精确键出现多个候选时返回 `ambiguous_match`，不会任选对象。
- 精确查询是批量只读预校验。候选结果只携带对象 ID、稳定键、组织编码、必要关联 ID 和范围判定，不读取或用于匹配名称、手机号、描述或模糊内容；预校验不调用外部系统，也不执行 `add`、`flush` 或 `commit`。
- 组织范围来自请求的 `AccessContext`：使用 `org_code`/`scope_roots` 的组织范围，并叠加员工本人范围和资产责任员工范围。文件不增加 `orgCode` 列。精确键存在但在范围外时逐行返回 `scope_denied`，不得将其预计为新增；真正不存在的完整行才可预计新增。

预计操作规则如下：

| 模板 | 精确匹配结果 | 预计操作 |
|---|---|---|
| `payload` | 资产标识匹配到资产 | `update` |
| `payload` | 资产标识均未匹配且必填完整 | `create` |
| `assignment` | 资产和员工均匹配 | `bind`/`transfer` 为 `update`，`unbind` 为 `skip` |
| `assignment` | 完整但资产或员工不存在 | `bind` 按既有行规则预计 `create`；`unbind`/`transfer` 缺资产或员工均报错 |
| `asset_payload_relation` | 资产和复合关系键均匹配 | `update` |
| `asset_payload_relation` | 资产匹配但复合关系键不存在 | `create` |

资产同时提供 `assetCode` 和 `carrierUid` 时，两者必须精确解析到同一资产；一方不存在、两者指向不同资产或任一方发生歧义/越权时整行报错。错误结果保留接口现有 Envelope、`requestId`、`rowNumber`、`status`、`operation`、`stableKey` 和 `errors` 字段结构。

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

每行至少提供 `assetCode` 或 `carrierUid` 一个。两者同时提供时，必须精确解析到同一个资产；如果一个已匹配而另一个不存在、匹配到其他资产或无法证明一致，整行报错，不能静默选择其中一个。两者均未匹配时，预校验可将该行标记为预计新增，但不会实际创建资产或内容。

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

`operation` 仅支持以下值；缺少该列或填写空值都不表达任何默认操作：

- `bind`：表达显式绑定意图。
- `unbind`：表达显式解绑意图。
- `transfer`：表达显式转交意图；跨组织转交仍需满足独立权限和数据范围规则。

`delete`、`disable`、`replace` 以及其他未列出的值不受支持。CSV 缺少某个既有绑定行不会触发解绑；只有该行明确填写 `unbind` 或 `transfer` 才能表达绑定关系变化意图。

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

当前模板层面的稳定关系描述为 `assetCode + payloadType + SHA-256(payloadValue)`；实际数据库探针使用对应资产 ID 和原始 `payloadValue` 做精确等值查询。不使用 `carrierUid` 代替 `assetCode`，也不使用载体或内容名称模糊匹配。示例：

```csv
assetCode,payloadValue,payloadType,payloadSource
TP-DEMO-001,https://example.invalid/demo,1,2
```

## 5. 组织和敏感数据边界

- `org_code` 是组织稳定业务键，用于后端数据权限和资产责任组织范围校验；V1.3.2 不新增 `orgCode` CSV 列。
- `employee_code` 是员工稳定业务键，不等同于姓名、手机号或 Casdoor 内部标识。
- 示例中的资产编码、UID、员工编码和内容均为脱敏固定值，不代表真实业务数据。
- CSV 内容、Token、JWT、Webhook Secret、数据库密码和未脱敏个人信息不得写入日志、错误消息、文档示例或测试输出。
