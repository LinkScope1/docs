# 前端组件规范

统一建设以下组件：

- `PageHeader`
- `SearchForm`
- `DataTable`
- `StatusTag`
- `ConfirmAction`
- `ScopeSelector`
- `ImportResult`
- `PublishStatus`
- `EmptyState`
- `ErrorState`
- `AuditDetail`

组件必须支持加载、空数据、错误和权限不足状态。业务页面不得复制一套新的分页、确认弹窗或错误提示逻辑。

## 公共 JS 交互和界面编号

- 公共 API 错误提示、成功提示、确认操作、提交锁定、分页、筛选、排序、加载、空数据、错误和无权限状态必须复用公共实现。
- 公共组件不得直接包含具体业务权限规则和业务接口 URL；业务规则由页面使用的领域 Service、Hook 或后台接口提供。
- 菜单统一使用以下稳定 `data-testid` 格式：

  ```text
  menu-{module}-{resource}
  ```

- 按钮统一使用以下稳定 `data-testid` 格式：

  ```text
  button-{module}-{resource}-{action}
  ```

- 示例：`menu-m2-organizations`、`button-m4-assignment-unbind`。
- `data-testid` 必须稳定、唯一，并且不依赖语言、页面顺序或 DOM 层级。
- `data-testid` 不得包含权限码、Token、手机号、姓名或其他敏感信息。
- 动态列表操作优先通过行定位后使用稳定按钮编号，不使用随机编号或不可重复的序号。
- 所有菜单项和业务操作按钮必须具备 `data-testid`，包括危险操作、导入、导出和权限不足状态。
