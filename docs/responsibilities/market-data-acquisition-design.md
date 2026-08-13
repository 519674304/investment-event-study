Document ID: RESP-MARKET
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: CTX-MARKET, RESP-MAP
Supersedes:

# 行情查询与缓存职责

## 目的与非目标

为一个证券身份和日期区间返回尽可能完整、合法的日线，并复用本地缓存。它不选择证券、不绘图、不搜索新闻。

## 公共合同

输入：`SecurityIdentity`、`DateRange`、是否更新到最新日期。  
输出：`MarketDataResult { BarSeries, Coverage, SourcesUsed, Issues }`。

## 内部流程

1. 读取本地覆盖范围并计算缺失区间。
2. 没有缺失时直接返回缓存。
3. 对每个缺失区间调用主行情端口。
4. 主源失败时调用备用端口。
5. 规范化字段、校验 OHLCV、按证券与日期去重。
6. 与已有缓存比较；冲突记录不静默覆盖。
7. 原子保存有效新增记录和覆盖元数据。
8. 返回实际覆盖范围、来源和结构化问题。

## 不变量与幂等性

- 相同请求重复执行不产生重复日线。
- 外部请求失败不改变已有缓存。
- 部分成功可以提交有效、不冲突记录，但返回 WARNING。
- 同一日期主备源冲突留待用户重试或后续规则处理，一期不做“多数表决”。

## 问题处理

- 主源不可用：MARKET/WARNING，降级备用源。
- 全部源不可用且缓存不足：MARKET/EXCEPTION，中止本次更新。
- 单条非法：MARKET/WARNING，跳过并报告日期。
- 大范围非法或身份不匹配：MARKET/EXCEPTION，不保存本批次。
- 本地保存失败：STORAGE/EXCEPTION，保留此前状态。

## 测试边界

使用假的主源、备用源和缓存端口验证：缓存命中、缺口计算、源切换、部分成功、冲突、非法 OHLCV、重复请求和保存失败。

## 备选方案

- 拒绝每次全量重查：浪费请求且无法离线复用。
- 拒绝把主备源直接串成永久混合序列：来源冲突不可审计。
