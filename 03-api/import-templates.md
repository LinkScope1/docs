# 导入模板规范

批量导入是横向能力，模板按业务对象分别定义。当前公开主数据模板不包含组织；组织主数据仍由组织管理接口维护。CSV 使用 UTF-8（兼容 UTF-8 BOM）；地址页面模板为 XLSX，以支持跳转类型下拉选择。表头必须完整、顺序固定，不允许缺列、重复列或未知列。

通用规则：

- 文件最大 10 MiB，最多 100,000 条数据行。
- 预校验：`POST /api/v1/imports/validate`。只读，不写业务表，不调用 LinkForty。
- 执行：`POST /api/v1/imports/execute`，必须携带 `Idempotency-Key`；1,000 行以内同步，超过 1,000 行落库后由 Celery 异步执行并返回 `202` 与 `batchId`。
- 批次查询：`GET /api/v1/imports/{batchId}`；失败报告：`GET /api/v1/imports/{batchId}/failure-report`。
- 每行独立事务；有稳定键的模板对同一文件重复键报错。资产模板是只新增操作、没有文件级资产匹配键；非空物理 UID 仅用于唯一性冲突检查，不作为选择既有资产更新的匹配键，重复 UID 报错。重复使用相同幂等键和相同请求返回原批次，不会因文件缺行删除、停用或解绑数据。资产行未填写物理 UID 时没有资产级去重键：改用新的幂等键再次导入会新建另一张卡；同一文件中多条 UID 为空的行也分别新建。
- 导入不承担员工绑定生命周期；绑定、解绑、转交使用绑定接口或批量绑定接口。

## 模板与字段约束

| 模板 | 下载类型 | 匹配/稳定键 | 必填字段 | 可空字段 |
| --- | --- | --- | --- | --- |
| 卡片 | `asset` | 无；只新增 | 责任组织编码 | 物理 UID、供应商编码、供应商批次、自定义短码、备注 |
| 载体内容 | `payload` | 内容 ID；新增时为卡ID/物理 UID + 内容类型 + 内容值 | 内容类型、内容值、内容来源；卡ID和物理 UID 至少一个 | 内容 ID、提供方、内容状态、卡ID或物理 UID（二选一仍至少一个） |
| 员工 | `employee` | 工号（`employees.employee_code`） | 姓名、工号、组织编码 | 联系方式（原手机号）、状态 |
| 地址页面 | `address_page`（XLSX） | 无；仅新建 | 地址标识、URL、跳转类型 | APP 专用字段、说明；APP 行按下方条件必填 |

## 卡片

下载：`GET /api/v1/imports/templates/assets` 或统一别名 `.../templates/asset`。

```csv
物理UID,责任组织编码,供应商编码,供应商批次,自定义短码,备注
```

卡片类型固定为 NFC；所有导入资产均以库存状态创建。资产导入只新增，不按卡ID或其他业务字段匹配和更新既有资产。模板没有资产编码或卡ID列，`asset_id` 由服务端根据 `Asia/Shanghai` 业务日期自动生成。物理 UID 可空；填写时仅用于全局唯一性冲突检查，重复 UID 拒绝新增，不会更新已存在的资产。没有 UID 的资产没有资产级去重保证：重传时必须复用同一个 `Idempotency-Key` 才会返回原导入批次；换用新键会生成新的资产和卡ID。责任组织必须存在、启用并在操作者数据范围内。自定义短码可空，最长 20 个字符，仅用于新资产的初始载体内容。卡片模板不允许提交责任员工。

## 载体内容

下载：`GET /api/v1/imports/templates/payloads` 或 `.../templates/payload`。

```csv
内容ID,内容类型,内容值,内容来源,提供方,内容状态,卡ID,物理UID
```

内容类型为 `短链`、`网址`、`文本`、`其他`；内容来源为 `供应商预写`、`本系统`、`外部导入`、`人工录入`；内容状态为 `待登记`、`有效`、`停用`、`失效`。新增时内容 ID 可空，修改时使用已有内容 ID。卡ID和物理 UID 至少填写一个，同时填写时必须指向同一张卡片。卡ID是业务字符串 `touchpoint_assets.asset_id`；Payload 的 `assetId` 仍是数值内部关联键。普通导入不允许用名称模糊匹配。

## 员工

下载：`GET /api/v1/imports/templates/employees`。

```csv
姓名,工号,组织编码,联系方式,状态
```

姓名、工号、组织编码不可为空；联系方式、状态可空。`工号` 映射数据库字段 `employees.employee_code`（也是 Casdoor `employee_code` Claim 的本地映射），不是系统生成的 `employee_uid`。联系方式映射原手机号字段；填写时必须为 11 位中国大陆手机号，入库加密，失败报告不回显完整号码。状态只能为 `启用` 或 `禁用`；新员工状态留空时按启用创建，已有员工留空时保留原值。Casdoor 同步任务不在本期导入闭环内，后续另行实现。

## 地址页面（统一 APP/网页/小程序模板）

下载：`GET /api/v1/imports/templates/address_pages` 或统一别名 `.../templates/address_page`。返回 XLSX，APP、网页和小程序共用一份模板；“跳转类型”列提供 `小程序`、`APP`、`网页` 下拉选项。固定表头为：

```text
地址标识,URL,跳转类型,APP iOS Scheme,APP Android Scheme,APP Harmony Scheme,APP Payload,APP回退地址,说明
```

字段规则：

- 此表只新建地址页面。模板不含地址编码、实际内容、组织编码；地址编码由服务端生成，不会通过导入更新已有页面。
- `地址标识`、`URL`、`跳转类型`：所有类型均不可为空。组织归属由后端根据当前导入人员的登录身份取得其组织并写入地址页面，不信任文件传入的组织值。
- `跳转类型` 只能为 `网页`、`小程序`、`APP`。网页/小程序的目标内容均取 `URL`；小程序 `URL` 必须为 HTTPS Universal Link。
- `APP iOS Scheme`、`APP Android Scheme`、`APP Harmony Scheme`：仅 APP 行使用，至少填写一个平台 Scheme。
- `APP Payload`：仅 APP 行使用，不可为空，最大 4,096 字符；只做非空和长度校验，不解析、不改写其内容。
- `APP回退地址`：仅 APP 行使用，不可为空，允许 HTTP 或 HTTPS 绝对地址；APP 行统一使用它作为目标配置。
- 网页/小程序行的所有 APP 专用列必须为空。
- `说明`：可空，最大 500 字符；URL 和 APP 回退地址最大 2,048 字符，平台 Scheme 最大 128 字符。

APP 页面最终目标继续使用既有拼接规则：由服务端用真实 LinkForty Link ID 生成 Bridge URL，并将 APP Payload 与平台 Scheme 作为不透明参数传入；模板中的 APP 回退地址只允许作为回退目标配置，不改变原有 Bridge 拼接规则。

## 绑定与批量配置

员工绑定不是主数据导入字段。专用生命周期导入模板下载为 `GET /api/v1/imports/templates/assignments`，执行为 `POST /api/v1/imports/assignments/execute`，固定表头为：

```csv
cardId,targetEmployeeCode,operation,reason
```

`cardId` 不可为空；`operation` 只能为 `bind`、`unbind`、`transfer`；`bind`/`transfer` 时 `targetEmployeeCode` 不可为空，`unbind` 时必须为空；`unbind`/`transfer` 时 `reason` 不可为空，最多 500 字符。该专用接口同步最多 1,000 行，失败按行返回。新建系统优先使用 `POST /api/v1/touchpoint-assets/batch-bind`、`batch-unbind`、`batch-configure`，这些 API 的 `assetId` 继续以内部 BIGINT ID 字符串传输；每个请求必须提供幂等键。`batch-configure` 的 `addressPageId` 必须显式传入，可使用 `null` 清空页面绑定；`employeeId` 同样可使用显式 `null` 清空员工绑定。批量配置页面时由服务端校验页面启用状态、组织层级、资产数据范围及 LinkForty 外部调用结果。

## 安全边界

预校验、失败报告和日志不得回显原始内容值、完整手机号、Token、密码、Webhook Secret 或数据库凭证。普通载体内容导出不包含原始内容值；受控原值导出需额外权限 `export.payload-content` 和二次确认。
