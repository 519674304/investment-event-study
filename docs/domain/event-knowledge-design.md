Document ID: CTX-EVENT
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: DOMAIN-MAP, REQ-EVENT, BASELINE-PRIMARY-FLOW
Supersedes:

# 事件知识上下文

## 目的与语言

保存用户已经确认的重要事实记录，使同一事件能够关联多个研究对象，并在不同对象的行情图上复用。

核心术语：事件草稿、已确认事件、真实发布日期、基础分类、自定义标签、对象关联、来源记录。

## 聚合与一致性

- 聚合根：`ConfirmedEvent`。
- 值对象：`PublicationDate`、`SourceReference`、`CategoryRef`、`Tag`、`ResearchObjectLink`。
- 事件本体和其全部对象关联作为一个一致性边界修改，避免部分对象显示旧内容。

## 不变量

- 必须有真实发布日期、非空标题和至少一个关联研究对象才能首次保存。
- 来源链接允许为空；为空时由展示层显示“来源未记录”。
- 一个事件实体可关联多个研究对象，修改后所有对象看到相同内容。
- 删除研究对象只解除关联；删除事件才删除事件本体及全部关联。
- `chartDate` 不是事件字段，避免行情区间或周期变化造成陈旧映射。
- 系统不保存自动领先/滞后或因果结论。

## 领域服务

- `DuplicateAssessment`：对草稿和已有事件生成重复提示，不强制阻止保存。
- `EventChartProjection`：接受事件和 `BarSeries`，计算图表映射日期、同日聚合和筛选结果；属于跨上下文只读领域协作。

## 事件事实

- `EventConfirmed`：用户首次确认保存。
- `EventRevised`：事件内容或关联变化。
- `EventDeleted`：用户确认删除事件。

这些事实用于同一进程内刷新各研究对象展示；一期不要求消息队列或跨服务投递。

## 覆盖需求

REQ-MANUAL-001—004、REQ-EVT-001—008、REQ-DETAIL-001—004、RULE-DATE-001—005。
