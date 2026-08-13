Document ID: PROJECT-INDEX
Status: Draft
Approved by:
Approved at:
Depends on:
Supersedes:

# 证券事件 K 线研究工具

## 项目目标

为单个研究者提供本地 Web 工具：按需查询 A 股股票、行业指数和概念指数的 K 线，把人工确认的外部关键信息按日期标记到图上，帮助研究者直接观察消息与价格变化的时间位置关系。

一期只解决资料整理与可视化，不由程序判断消息是否领先、同步或滞后，也不进行公司基本面、行业供需或估值分析。公司系统分析列入二期。

## 当前阶段

Phase 5：实施计划已批准，进入实施。

## 阶段审批

| 阶段 | 状态 | 审批人 | 审批日期 |
| --- | --- | --- | --- |
| Phase 0：上下文探索 | Completed | 对话确认 | 2026-08-12 |
| Phase 1：需求 | Approved | 用户 | 2026-08-12 |
| Phase 2：领域与职责设计 | Approved | 用户 | 2026-08-12 |
| Phase 3：生命周期与扩展设计 | Approved | 用户 | 2026-08-12 |
| Phase 4：技术与架构 | Approved | 用户 | 2026-08-12 |
| Phase 5：实施计划 | Approved | 用户 | 2026-08-12 |

## 文档目录

- [需求总览](requirements/00-overview.md)
- [范围与约束](requirements/01-scope-and-constraints.md)
- [研究对象与行情图需求](requirements/02-research-object-and-chart.md)
- [信息搜索与事件管理需求](requirements/03-information-and-events.md)
- [主流程输入输出基线](baselines/README.md)
- [领域总图](domain/00-domain-map.md)
- [研究目录上下文](domain/research-catalog-design.md)
- [行情上下文](domain/market-data-design.md)
- [信息发现上下文](domain/information-discovery-design.md)
- [事件知识上下文](domain/event-knowledge-design.md)
- [职责总图](responsibilities/00-responsibility-map.md)
- [行情查询与缓存职责](responsibilities/market-data-acquisition-design.md)
- [信息搜索与确认职责](responsibilities/information-capture-design.md)
- [事件图表投影职责](responsibilities/event-chart-projection-design.md)
- [生命周期与扩展模型](architecture/00-lifecycle-and-extension-model.md)
- [技术选型](architecture/01-technical-selection.md)
- [技术架构](architecture/02-technical-architecture.md)
- [实施路线图](plans/00-roadmap.md)
- [行情实施计划](plans/market-data-plan.md)
- [信息与事件实施计划](plans/information-and-events-plan.md)
- [K线与事件交互实施计划](plans/chart-interaction-plan.md)
- [Windows 发布实施计划](plans/windows-release-plan.md)

## 依赖关系

```text
REQ-OVERVIEW
  -> REQ-SCOPE
  -> REQ-CHART
  -> REQ-EVENT
  -> BASELINE-PRIMARY-FLOW
  -> CTX-CATALOG / CTX-MARKET / CTX-DISCOVERY / CTX-EVENT
  -> RESP-MAP
```

## 开放事项

- 免费行情主源与备用源的具体选择留到 Phase 4。
- 免费信息搜索渠道及可用性降级方式留到 Phase 4。
- 本地持久化技术和 Windows 启动方式的具体实现留到 Phase 4。

## 已替代文档

- `docs/superpowers/specs/2026-08-12-hog-sector-884275-event-chart-design.md` 是一次性生猪指数图表设计，已被本通用工具需求替代，不再作为实施依据。
