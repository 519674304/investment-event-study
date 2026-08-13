Document ID: PLAN-CHART
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: PLAN-MARKET-002, PLAN-CATALOG-EVENT-001, RESP-PROJECTION, ARCH-TECHNICAL
Supersedes:

# K线与事件交互实施计划

## PLAN-CHART-001：事件图表投影

- 需求：RULE-DATE-001—005、REQ-CHART-004—007、REQ-DETAIL-001—004。
- 上下文/职责：CTX-MARKET、CTX-EVENT、RESP-PROJECTION。
- ADR：ADR-002、ADR-004。
- 目标：从行情和事件稳定生成日/周/月投影，非交易日只映射到此前 K 线，同一行情条聚合。
- 文件：`backend/events/domain/projection.py`、应用查询/API DTO、属性测试和基线契约测试。
- 步骤：用测试覆盖二分查找映射；增加周期归属、分类标签过滤和同柱聚合；对空/无序行情返回结构化问题；用批准 JSON 基线固定输出。
- 测试：交易日、周末、春节长假、停牌、首条行情前、范围外、同日多事件、周/月周期和5,000事件性能。
- 完成证据：基线中的 `2026-08-09` 映射为 `2026-08-07`，真实日期不被修改；无自动判断字段。

## PLAN-CHART-002：研究页面 K线和双向定位

- 需求：REQ-CHART-001—008、AC-CHART-001—005、REQ-PERF-001。
- 上下文/职责：RESP-PERIOD、RESP-PROJECTION、RESP-PRESENT。
- ADR：ADR-003、ADR-004。
- 依赖：PLAN-CHART-001、PLAN-MARKET-003。
- 文件：React 研究页面、ECharts 封装、事件过滤器、详情列表、页面状态 API 和组件/E2E 测试。
- 步骤：先显示真实 K 线和成交量；加入日周月切换和缩放；加入聚合事件标记；实现图点→下方详情与详情→图点；保存每对象最后状态；处理最新请求和取消。
- 测试：红涨绿跌、OHLC tooltip、缩放、筛选、同日聚合、双向定位、响应乱序、重启恢复和窄屏可用性。
- 性能：用10年日线+5,000事件测量数据转换、ECharts 首次完成和筛选更新时间。
- 完成证据：CP-3 截图/录像及性能结果。
