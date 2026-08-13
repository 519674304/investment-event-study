Document ID: CTX-CATALOG
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: DOMAIN-MAP, REQ-CHART
Supersedes:

# 研究目录上下文

## 目的与语言

管理研究者已经关注的证券对象。一个可交易或可观察证券身份只对应一个研究对象，不存在多个命名视图。

核心术语：证券候选、证券身份、研究对象、对象类型、最后研究状态。

## 拥有能力和数据

- 按代码或名称接收外部证券候选。
- 根据规范化证券身份创建或打开唯一研究对象。
- 列出和删除研究对象。
- 保存每个对象最后的日期范围、K 线周期、事件筛选和图表位置。

## 聚合与规则

- 聚合根：`ResearchObject`。
- 值对象：`SecurityIdentity`（市场、代码、类型）、`ResearchState`。
- 不变量：同一 `SecurityIdentity` 最多存在一个研究对象。
- 删除对象只删除本对象及其事件关联关系请求，不拥有也不删除事件实体或行情实体。

## 合同

- 输入：外部 `SecurityCandidate`、研究状态修改、删除请求。
- 输出：稳定 `ResearchObjectRef`、对象列表、最后状态。
- 上游：证券检索适配器。
- 下游：CTX-MARKET、CTX-DISCOVERY、CTX-EVENT。

## 失败与补偿

- 同名候选不自动选取，由用户选择。
- 重复创建返回现有对象，不报冲突错误。
- 删除对象时若解除事件关联失败，整个删除操作不得提交。

## 覆盖需求

REQ-OBJ-001—005、REQ-CHART-008、REQ-REL-001—002。
