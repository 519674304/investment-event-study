Document ID: PLAN-MARKET
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: PLAN-FOUNDATION-001, CTX-MARKET, RESP-MARKET, ARCH-TECHNICAL
Supersedes:

# 行情实施计划

## PLAN-MARKET-001：免费源契约探针

- 需求：REQ-OBJ-001—003、REQ-DATA-001—004、REQ-MKT-003—005。
- 上下文/职责：CTX-CATALOG、CTX-MARKET、RESP-OBJECT、RESP-MARKET。
- ADR：ADR-006。
- 目标：在写生产适配器前，用可重复脚本验证股票、行业指数、同花顺概念指数的候选搜索及历史 OHLCV 能力。
- 文件：`tools/provider_probe/`、`tests/fixtures/providers/`、`docs/project/evidence/provider-probe.md`。
- 步骤：定义来源响应样本；验证 `002714`、一个行业指数、`884275`；记录首末日期、字段、限频和失败形态；选择每类对象的主/备路由；没有备用时显式记录。
- 测试：离线样本契约测试 + 可显式运行的在线烟雾测试，不把在线测试放进默认单元测试。
- 失败处理：若某类对象无免费可用源，停止该类生产适配并回到需求审批，不以近似对象替代。
- 完成证据：三类对象的探针报告和固定响应样本。

## PLAN-MARKET-002：行情领域与持久缓存

- 需求：REQ-MKT-001—005、REQ-PERF-001—003、REQ-REL-004。
- 上下文/职责：CTX-MARKET、RESP-MARKET。
- ADR：ADR-002、ADR-005、ADR-006。
- 依赖：PLAN-MARKET-001。
- 文件：`backend/market/domain/`、`backend/market/application/`、`backend/market/infrastructure/repository.py`、迁移和测试。
- 合同/数据：`MarketDataProvider`、`MarketSeriesRepository`、`BarSeries`、`Coverage`；日线证券+日期唯一；来源和更新时间可审计。
- 步骤：测试先定义 OHLCV、缺口和合并规则；实现日线验证与周/月聚合；实现 SQLite 仓储和覆盖检查；实现同证券更新锁与原子批次提交。
- 测试：非法 OHLC、重复日期、部分覆盖、跨年缺口、幂等重试、并行重叠请求、事务失败。
- 回滚：批次保存失败回滚，旧缓存保持；迁移有 downgrade 或恢复脚本。
- 完成证据：离线假源下只请求缺口，并从日线稳定生成周/月线。

## PLAN-MARKET-003：生产适配器与 API

- 需求：REQ-DATA-002—004、REQ-MKT-001—005、AC-CORE-001。
- 上下文/职责：RESP-MARKET、RESP-OBJECT。
- ADR：ADR-002、ADR-006。
- 依赖：PLAN-MARKET-002。
- 文件：`backend/catalog/infrastructure/providers/`、`backend/market/infrastructure/providers/`、API 路由和契约测试。
- 步骤：按探针结果实现证券搜索适配；实现各证券类型行情适配；实现有序回退策略；API 返回实际覆盖、数据截止和结构化问题；加入超时、响应大小和内容校验。
- 测试：固定样本契约、主源失败切备源、无备用明确提示、全部失败仍返回可用缓存、不可信字段防护。
- 完成证据：真实创建股票、行业和概念对象并加载指定区间；日志显示实际来源。
