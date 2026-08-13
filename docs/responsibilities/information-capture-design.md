Document ID: RESP-INFORMATION-CAPTURE
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: CTX-DISCOVERY, CTX-EVENT, RESP-MAP
Supersedes:

# 信息搜索与确认职责

## 目的

把用户主动搜索得到的临时候选或手工输入，经过编辑、重复提示和明确确认后转化为持久化事件。

## 公共合同

- `search(objectSnapshot, dateRange, keywords, page)` → `SearchPage`。
- `prepare(candidate | manualInput)` → 可编辑 `EventDraft`。
- `assessDuplicate(draft)` → `DuplicateHint[]`。
- `confirm(draft, userDecision)` → `ConfirmedEvent` 或取消结果。

## 工作流

1. 由用户动作创建搜索会话，组合对象名称、代码、日期和附加关键词。
2. 请求指定页并规范化标题、日期、来源、摘要和链接。
3. 结果只保留在当前会话；离开或取消后丢弃。
4. 用户选择候选或进入手工补录，形成草稿。
5. 校验真实日期、标题和至少一个对象；缺失可选字段不阻止保存。
6. 与已有事件比较链接、标题和邻近日期，返回重复提示。
7. 用户仍可确认；确认后调用事件上下文一次性保存。

## 并发和幂等

- 重复点击“加载下一页”不得在当前结果列表产生相同候选副本。
- 保存按钮在一次确认进行中禁用重复提交。
- 系统不依赖自动去重保证唯一性，因为业务允许用户有意保存近似事件。

## 问题处理

- 搜索源失败：SEARCH/EXCEPTION，仅中止当前页请求。
- 候选缺日期：SEARCH/WARNING，允许用户补充后保存。
- 疑似重复：DUPLICATE/WARNING，要求用户确认继续或取消。
- 事件保存失败：EVENT 或 STORAGE/EXCEPTION，草稿留在编辑状态便于重试。

## 测试边界

使用假搜索端口和事件仓储测试分页、候选临时性、字段规范化、重复提示、用户覆盖提示、手工无链接事件以及重复提交。

## 明确排除

不抓全文、不自动总结、不后台搜索、不自动保存、不判断消息影响。
