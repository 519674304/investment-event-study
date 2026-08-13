Document ID: PLAN-ROADMAP
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: REQ-OVERVIEW, DOMAIN-MAP, RESP-MAP, ARCH-LIFECYCLE, ARCH-SELECTION, ARCH-TECHNICAL
Supersedes:

# 一期实施路线图

## 范围和批准输入

实施范围严格限于已批准的一期：A 股股票、行业指数和概念指数；按需 K 线；联网搜索人工确认；手工补录；事件多对象关联；图上标记及下方详情；本机持久化和 Windows 双击启动。自动领先/滞后判断和公司系统分析不进入实施。

## 执行顺序

```text
M0 工程与契约骨架
 -> M1 本地研究目录与事件存储
 -> M2 真实证券搜索、行情主备与缓存
 -> M3 K线研究页面与事件投影
 -> M4 信息搜索、人工确认和手工补录
 -> M5 恢复、可观测性、Windows发布
 -> M6 全流程验收
```

每个里程碑必须产生可运行纵向切片，不允许先搭建全部“基础设施”而长期没有可操作页面。

## M0：工程、基线和边界

### PLAN-FOUNDATION-001

- 需求：REQ-SEC-001—003、BASELINE-PRIMARY-FLOW。
- 上下文/职责：DOMAIN-MAP、RESP-MAP。
- ADR：ADR-001、ADR-002、ADR-003、ADR-005。
- 目标：建立后端、前端、迁移、测试和统一问题合同的最小骨架，并能从一个进程提供前端和 `/api/health`。
- 具体变化：新增 `app/backend/`、`app/frontend/`、`app/migrations/`、`app/tests/`、构建配置和开发启动脚本；定义 `TIP/WARNING/EXCEPTION` DTO。
- 顺序：先写健康接口与问题合同测试，再建立最小 FastAPI；再建立 React 空壳并由后端提供构建资源；最后接入临时 SQLite 和首个迁移。
- 测试：后端单元/API 测试、前端构建测试、数据库迁移往返测试。
- 回滚：骨架没有用户数据；失败时删除新增构建产物，不修改既有研究文档。
- 完成证据：一条命令运行测试；开发启动后浏览器显示首页骨架；健康接口报告版本和迁移版本。

## M1：研究对象与事件本地闭环

### PLAN-CATALOG-EVENT-001

- 需求：REQ-OBJ-001—005（候选先使用假适配器）、REQ-EVT-001—008、REQ-MANUAL-001—004、REQ-REL-001—003。
- 上下文/职责：CTX-CATALOG、CTX-EVENT、RESP-OBJECT、RESP-STATE、RESP-EVENT。
- ADR：ADR-002、ADR-003、ADR-005。
- 目标：不用外部网络也能创建唯一对象、手工新增/编辑/删除事件、多对象关联并重启恢复。
- 具体变化：研究对象、状态、事件、分类、标签和关联的领域模型、仓储、迁移、API 与首页/事件编辑 UI。
- 数据变化：创建研究对象、状态、事件、分类、标签、多对多关联表及唯一/外键约束；种子化基础分类。
- 测试：对象唯一性、删除对象只解关联、事件事务修改、无链接事件、重启恢复、XSS 字符转义。
- 错误与回滚：所有跨表修改使用事务；迁移前备份由 M5 完成，一期首次初始化失败不得创建半结构数据库。
- 完成证据：两个研究对象关联同一手工事件，重启后仍存在；删除一个对象不删除事件。

## M2—M5 详细计划

- [行情实施计划](market-data-plan.md)：PLAN-MARKET-001—003。
- [K线与事件交互实施计划](chart-interaction-plan.md)：PLAN-CHART-001—002。
- [信息与事件实施计划](information-and-events-plan.md)：PLAN-INFO-001—003。
- [Windows 发布实施计划](windows-release-plan.md)：PLAN-RELEASE-001—003。

## M6：最终验收

### PLAN-ACCEPTANCE-001

- 需求：AC-CORE-001—004、全部 `AC-CHART-*` 与 `AC-EVT-*`。
- 上下文/职责：全部一期上下文与职责。
- ADR：ADR-001—008。
- 依赖：M0—M5 全部完成。
- 目标：在干净 Windows 用户环境执行完整主流程和异常恢复。
- 测试数据：关键基线 JSON、一个 A 股股票、一个行业指数、一个概念指数、一个周末事件、一个多对象事件、一个无链接事件。
- 验收步骤：双击启动；名称/代码建对象；查询 10 年日线并切换周/月；联网搜索分页并编辑确认；手工补录；筛选与双向定位；重启；删除对象验证事件保留；模拟主源失败、信息源失败和缓存部分覆盖。
- 性能：缓存命中后 10 年日线 + 5,000 事件的首屏 3 秒内，记录机器配置、API 时间、投影时间和浏览器完成时间。
- 完成证据：自动测试报告、Windows 端到端录像或截图、性能报告、数据源在线烟雾测试结果及已知限制。

## 集成检查点

- CP-1：M1 后确认本地数据模型和“事件可未关联保留”的行为。
- CP-2：M2 后确认三种证券类型至少各有一个真实行情样例，不允许概念指数被近似替代。
- CP-3：M3 后用周末事件验证图上落点和真实日期同时显示。
- CP-4：M4 后确认未选搜索结果重启后不存在。
- CP-5：M5 后在不安装开发工具的 Windows 用户环境双击启动。

## 风险与技术探针

1. 免费源稳定性最高风险：M2 首项先做在线契约探针，确认证券搜索和三类对象的历史 OHLCV。
2. 免费网页搜索可能反爬或缺日期：M4 先做搜索源探针；失败不能阻塞手工事件闭环。
3. 5,000 事件图上直接渲染可能拥挤：M3 用合成数据验证聚合与筛选性能。
4. Windows 打包体积和杀毒误报：M5 先制作最小启动包再集成完整应用。

## 完整需求到计划与测试追踪

下表中的“测试”是对应计划内必须实现的自动化或验收测试，不以人工说明替代。

| 需求与验收 ID | 实施计划 | 测试证据 |
| --- | --- | --- |
| REQ-OBJ-001、REQ-OBJ-002、REQ-OBJ-003、REQ-OBJ-004、REQ-OBJ-005 | PLAN-CATALOG-EVENT-001、PLAN-MARKET-003 | 候选搜索契约；唯一对象、列表、打开和删除集成测试 |
| REQ-MKT-001、REQ-MKT-002、REQ-MKT-003、REQ-MKT-004、REQ-MKT-005 | PLAN-MARKET-001、PLAN-MARKET-002、PLAN-MARKET-003 | 缺口、OHLCV、主备降级、覆盖和截止日测试 |
| REQ-CHART-001、REQ-CHART-002、REQ-CHART-003、REQ-CHART-004、REQ-CHART-005、REQ-CHART-006、REQ-CHART-007、REQ-CHART-008 | PLAN-CHART-001、PLAN-CHART-002 | K线组件、筛选、聚合、双向定位和状态恢复测试 |
| RULE-DATE-001、RULE-DATE-002、RULE-DATE-003、RULE-DATE-004、RULE-DATE-005 | PLAN-CHART-001 | 交易日、周末、节假日、停牌和周/月映射参数化测试 |
| REQ-SEARCH-001、REQ-SEARCH-002、REQ-SEARCH-003、REQ-SEARCH-004、REQ-SEARCH-005、REQ-SEARCH-006、REQ-SEARCH-007 | PLAN-INFO-001、PLAN-INFO-002 | 显式触发、查询生成、字段、20条分页、临时性和失败测试 |
| REQ-DUP-001、REQ-DUP-002、REQ-DUP-003、REQ-DUP-004 | PLAN-INFO-002 | 链接、标题日期、对象近似和用户覆盖测试 |
| REQ-CONFIRM-001、REQ-CONFIRM-002、REQ-CONFIRM-003 | PLAN-INFO-002 | 保存前编辑、确认和取消端到端测试 |
| REQ-MANUAL-001、REQ-MANUAL-002、REQ-MANUAL-003、REQ-MANUAL-004 | PLAN-CATALOG-EVENT-001、PLAN-INFO-003 | 必填、可选字段、无链接和一致行为测试 |
| REQ-EVT-001、REQ-EVT-002、REQ-EVT-003、REQ-EVT-004、REQ-EVT-005、REQ-EVT-006、REQ-EVT-007、REQ-EVT-008 | PLAN-CATALOG-EVENT-001、PLAN-INFO-003 | 单事件多对象、同步修改、删除、分类标签、持久化与排除项测试 |
| REQ-DETAIL-001、REQ-DETAIL-002、REQ-DETAIL-003、REQ-DETAIL-004 | PLAN-INFO-003、PLAN-CHART-002 | 图下详情字段、来源缺失、日期排序和双向定位测试 |
| REQ-DATA-001、REQ-DATA-002、REQ-DATA-003、REQ-DATA-004、REQ-DATA-005、REQ-DATA-006 | PLAN-MARKET-001、PLAN-MARKET-003、PLAN-INFO-001、PLAN-INFO-003 | 免费源探针、源隔离、失败提示、持久字段和无链接测试 |
| REQ-PERF-001、REQ-PERF-002、REQ-PERF-003、REQ-PERF-004 | PLAN-MARKET-002、PLAN-INFO-002、PLAN-CHART-002、PLAN-ACCEPTANCE-001 | 10年日线/5000事件基准、加载状态和20条分页测试 |
| REQ-REL-001、REQ-REL-002、REQ-REL-003、REQ-REL-004 | PLAN-CATALOG-EVENT-001、PLAN-MARKET-002、PLAN-RELEASE-002、PLAN-ACCEPTANCE-001 | 重启、对象删除、事件删除、外部失败不破坏本地数据测试 |
| REQ-SEC-001、REQ-SEC-002、REQ-SEC-003 | PLAN-FOUNDATION-001、PLAN-RELEASE-001、PLAN-RELEASE-002 | 仅本机监听、无凭据、XSS/HTML转义和日志脱敏测试 |
| AC-CORE-001、AC-CORE-002、AC-CORE-003、AC-CORE-004 | PLAN-ACCEPTANCE-001 | Windows 全主流程端到端验收 |
| AC-CHART-001、AC-CHART-002、AC-CHART-003、AC-CHART-004、AC-CHART-005 | PLAN-CHART-002、PLAN-ACCEPTANCE-001 | 三类对象、三周期、增量缓存、周末映射、同柱聚合验收 |
| AC-EVT-001、AC-EVT-002、AC-EVT-003、AC-EVT-004、AC-EVT-005、AC-EVT-006 | PLAN-INFO-002、PLAN-INFO-003、PLAN-ACCEPTANCE-001 | 分页临时性、编辑、重复、无链接、多对象和筛选验收 |
