Document ID: PLAN-INFORMATION-EVENTS
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: PLAN-CATALOG-EVENT-001, RESP-INFORMATION-CAPTURE, ARCH-TECHNICAL
Supersedes:

# 信息搜索与事件实施计划

## PLAN-INFO-001：免费信息搜索探针

- 需求：REQ-SEARCH-001—007、REQ-DATA-001、REQ-DATA-005。
- 上下文/职责：CTX-DISCOVERY、RESP-SEARCH。
- ADR：ADR-006。
- 目标：验证无需账号密钥的公开搜索入口能否按证券、日期和关键词返回标题、日期、来源、摘要和链接，并记录缺失字段比例。
- 文件：`tools/search_probe/`、`tests/fixtures/search/`、`docs/project/evidence/search-provider-probe.md`。
- 测试：固定样本解析、分页、无日期、重复页、超时和页面格式变化；在线测试显式运行。
- 失败处理：若无可靠搜索源，一期发布仍保留手工补录，但必须回到用户审批是否接受“搜索为实验功能”，不得伪装完成 AC-CORE-002。
- 完成证据：探针报告、选定适配合同和降级说明。

## PLAN-INFO-002：搜索会话与候选编辑

- 需求：REQ-SEARCH-001—007、REQ-DUP-001—004、REQ-CONFIRM-001—003。
- 上下文/职责：CTX-DISCOVERY、RESP-SEARCH、RESP-CAPTURE。
- ADR：ADR-002、ADR-003、ADR-006。
- 依赖：PLAN-INFO-001。
- 文件：后端搜索会话/适配器/API、前端搜索面板、候选列表和编辑表单、测试。
- 合同：内存 `SearchSession`、20 条 `SearchPage`、`InformationCandidate`、`DuplicateHint`、`EventDraft`。
- 步骤：先实现假搜索端到端；再接生产适配器；增加下一页、会话过期、候选指纹；加入保存前字段编辑和重复确认。
- 测试：用户未点击不请求、每页20、改变条件使旧会话失效、未确认不入库、相同链接和相似标题提示但可覆盖。
- 完成证据：联网搜索一页和下一页；选择、编辑并确认后只保存一条事件；重启后未选结果不存在。

## PLAN-INFO-003：事件管理完整交互

- 需求：REQ-MANUAL-001—004、REQ-EVT-001—008、REQ-DETAIL-001—004、AC-CORE-002—004。
- 上下文/职责：CTX-EVENT、RESP-CAPTURE、RESP-EVENT、RESP-PRESENT。
- ADR：ADR-003、ADR-005。
- 依赖：PLAN-CATALOG-EVENT-001、PLAN-INFO-002。
- 文件：事件 API、编辑/删除/关联 UI、基础分类种子、自定义标签控件、下方详情组件。
- 步骤：完善手工补录；实现事件检索与未关联事件复用；实现多对象关联编辑；实现删除确认；详情区显示来源缺失状态和安全链接。
- 测试：一个事件关联三对象、修改同步、对象删除事件保留、事件删除全局消失、无链接显示、分类/标签持久化和 XSS 输入。
- 回滚：所有事件与关联修改单事务；失败时表单保留可重试。
- 完成证据：满足 AC-EVT-001—006 的自动化和端到端证据。
