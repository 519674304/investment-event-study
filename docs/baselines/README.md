Document ID: BASELINE-PRIMARY-FLOW
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: REQ-OVERVIEW, REQ-SCOPE, REQ-CHART, REQ-EVENT
Supersedes:

# 主流程输入输出基线

## 文件

- `primary-flow-input.json`：用户打开生猪养殖概念指数，查询指定时间段并确认一条周末发布的信息。
- `expected-output.json`：系统保存研究对象、行情覆盖范围和事件，并把周末事件映射到此前最近交易日。

## 映射关系

- `researchObject.candidateId` 产生输出中的稳定 `researchObject.id`。
- 输入事件 `draftId` 只用于保存前会话；确认后产生稳定 `event.id`。
- `event.publishedOn` 原样保存为真实发布日期。
- `event.chartDate` 从已查询 K 线中选择不晚于真实发布日期的最近日期。
- `linkedResearchObjectIds` 表示一个事件可供多个研究对象复用。
- 输出只陈述保存和映射结果，不包含领先、同步、滞后或交易判断。

## 稳定 ID 的业务含义

- `researchObject.id`：本地唯一研究对象，一个证券只能对应一个。
- `event.id`：本地唯一事件，可关联多个研究对象。
- `category.id`：基础分类稳定标识，用于跨对象筛选。
