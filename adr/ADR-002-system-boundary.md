# ADR-002：银行后台与 LinkForty Core 分离

## 状态

Accepted

## 决策

银行后台作为独立 Python 服务建设，LinkForty Core 继续负责短链平台和原始事件。

## 规则

- 银行后台不直接修改 LinkForty 表。
- LinkForty 写入必须通过 API。
- M7/M8 使用受限只读访问读取必要事件。
- 前端只调用银行后台 API。
