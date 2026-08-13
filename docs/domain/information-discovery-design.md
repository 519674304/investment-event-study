Document ID: CTX-DISCOVERY
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: DOMAIN-MAP, REQ-EVENT
Supersedes:

# 信息发现上下文

## 目的与边界

根据研究对象、日期范围和附加关键词联网寻找可能相关的信息，供用户筛选。它只产生临时候选，不拥有已确认事件。

## 模型

- 会话根：`SearchSession`，只存在于当前搜索会话。
- 值对象：`SearchQuery`、`InformationCandidate`、`SearchPage`、`DuplicateHint`。
- 候选字段：标题、发布日期、来源名称、简短摘要、原文链接。

## 规则

- 搜索只能由用户显式触发。
- 默认条件来自当前研究对象和日期范围，用户可追加关键词。
- 每页 20 条，按日期倒序；下一页只在用户请求时获取。
- 未确认候选不持久化，也不能出现在 K 线上。
- 重复判断只产生提示：相同链接、近日期高相似标题或当前对象已有近似事件；不得自动合并。

## 合同与关系

- 输入：`ResearchObjectSnapshot + DateRange + Keywords + PageRequest`。
- 输出：临时 `SearchPage`。
- 用户选中候选并编辑后，应用层把它转换为 CTX-EVENT 接受的 `EventDraft`。
- CTX-DISCOVERY 可读取事件指纹进行重复提示，但不能修改事件。

## 失败

- 搜索源失败：返回可重试异常，不产生空白伪结果。
- 部分字段缺失：若仍有标题和链接可展示，则以警告返回；发布日期缺失的候选不能直接保存，必须由用户补充。

## 覆盖需求

REQ-SEARCH-001—007、REQ-DUP-001—004、REQ-CONFIRM-001—003。
