Document ID: RESP-MAP
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: DOMAIN-MAP, CTX-CATALOG, CTX-MARKET, CTX-DISCOVERY, CTX-EVENT
Supersedes:

# 职责总图

## 职责表

| ID | 职责 | 上下文 | 输入 → 输出 | 依赖 | 复杂度 |
| --- | --- | --- | --- | --- | --- |
| RESP-OBJECT | 创建、打开、列出和删除唯一研究对象 | CTX-CATALOG | 候选/命令 → 对象引用 | 证券检索端口、关联解除端口 | 简单 |
| RESP-STATE | 保存并恢复对象最后研究状态 | CTX-CATALOG | 状态修改 → 状态快照 | 本地持久化端口 | 简单 |
| RESP-MARKET | 查询、校验、合并和缓存行情 | CTX-MARKET | 对象+区间 → BarSeries | 主/备行情端口、缓存端口 | 复杂，见详细文档 |
| RESP-PERIOD | 日线聚合为周/月线 | CTX-MARKET | DailyBars+周期 → BarSeries | 无外部依赖 | 简单 |
| RESP-SEARCH | 生成查询、分页搜索并规范化候选 | CTX-DISCOVERY | 对象+区间+关键词 → SearchPage | 信息搜索端口 | 复杂，见详细文档 |
| RESP-CAPTURE | 搜索候选编辑确认或手工补录 | CTX-DISCOVERY/CTX-EVENT | 候选/手工输入 → EventDraft → ConfirmedEvent | 事件仓储、重复评估 | 复杂，见详细文档 |
| RESP-EVENT | 新增、编辑、删除事件及对象关联 | CTX-EVENT | 事件命令 → 事件快照 | 事件仓储、对象引用查询 | 简单 |
| RESP-PROJECTION | 把事件映射、聚合和筛选到 K 线 | CTX-EVENT/CTX-MARKET | Events+BarSeries+Filter → Projection | 无外部依赖 | 复杂，见详细文档 |
| RESP-PRESENT | 呈现首页、K线、搜索选择和下方详情 | 应用边界 | 只读视图模型/用户命令 | 上述应用合同 | 简单，不拥有业务规则 |

## 依赖方向

```text
UI -> 应用职责 -> 领域上下文定义的合同
                     ^
                     |
         外部行情/搜索/持久化适配器
```

UI 不直接调用外部数据源，不计算事件映射，不判断重复，不直接操作存储。

## 结构化问题分类

| 分类 | 典型来源 | 接收职责 | 继续策略 |
| --- | --- | --- | --- |
| OBJECT | 证券候选不明确、对象无效 | RESP-OBJECT | WARNING：等待用户选择；EXCEPTION：中止创建 |
| MARKET | 源失败、覆盖不完整、行情非法 | RESP-MARKET | WARNING：降级/部分成功；EXCEPTION：保留旧缓存并中止本次更新 |
| SEARCH | 搜索失败、候选缺字段 | RESP-SEARCH | WARNING：跳过或要求补充；EXCEPTION：中止当前搜索页 |
| DUPLICATE | 疑似重复事件 | RESP-CAPTURE | WARNING：继续，由用户决定 |
| EVENT | 事件验证或关联失败 | RESP-EVENT | EXCEPTION：不提交修改 |
| PROJECTION | 事件无可用此前 K 线 | RESP-PROJECTION | TIP：不显示标记，事件仍保留 |
| STORAGE | 本地读写失败 | 发起操作的应用职责 | EXCEPTION：保持上一个有效状态 |

严重度统一为：TIP 继续并按需提示；WARNING 继续、跳过或降级并明确展示；EXCEPTION 中止当前操作、保留最后有效状态。产生职责输出结构化问题，不拼 UI 文案；应用边界转换为用户可读提示。

## 需求追踪摘要

- RESP-OBJECT / RESP-STATE：REQ-OBJ-001、REQ-OBJ-002、REQ-OBJ-003、REQ-OBJ-004、REQ-OBJ-005、REQ-CHART-008。
- RESP-MARKET / RESP-PERIOD：REQ-MKT-001、REQ-MKT-002、REQ-MKT-003、REQ-MKT-004、REQ-MKT-005、REQ-CHART-001、REQ-CHART-002、REQ-CHART-003。
- RESP-SEARCH：REQ-SEARCH-001、REQ-SEARCH-002、REQ-SEARCH-003、REQ-SEARCH-004、REQ-SEARCH-005、REQ-SEARCH-006、REQ-SEARCH-007、REQ-DUP-001、REQ-DUP-002、REQ-DUP-003、REQ-DUP-004。
- RESP-CAPTURE / RESP-EVENT：REQ-CONFIRM-001、REQ-CONFIRM-002、REQ-CONFIRM-003、REQ-MANUAL-001、REQ-MANUAL-002、REQ-MANUAL-003、REQ-MANUAL-004、REQ-EVT-001、REQ-EVT-002、REQ-EVT-003、REQ-EVT-004、REQ-EVT-005、REQ-EVT-006、REQ-EVT-007、REQ-EVT-008。
- RESP-PROJECTION / RESP-PRESENT：RULE-DATE-001、RULE-DATE-002、RULE-DATE-003、RULE-DATE-004、RULE-DATE-005、REQ-CHART-004、REQ-CHART-005、REQ-CHART-006、REQ-CHART-007、REQ-DETAIL-001、REQ-DETAIL-002、REQ-DETAIL-003、REQ-DETAIL-004。
