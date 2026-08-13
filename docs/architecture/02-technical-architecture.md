Document ID: ARCH-TECHNICAL
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: ARCH-LIFECYCLE, ARCH-SELECTION, DOMAIN-MAP, RESP-MAP
Supersedes:

# 技术架构

## 运行组件

```text
Windows 启动器
  -> FastAPI 本地进程（仅 127.0.0.1，动态端口）
       -> 静态前端 React/Vite
       -> 应用用例层
       -> 领域层
       -> SQLite 仓储
       -> 行情/证券搜索适配器 -> 免费行情源
       -> 信息搜索适配器     -> 免费搜索源与网页
  -> 默认浏览器
```

单一后端进程同时提供 API 和前端静态资源，避免跨域配置和多个启动窗口。

## 分层与依赖

```text
UI (React/ECharts)
  -> API DTO
Application Use Cases
  -> Domain Models and Ports
Infrastructure Adapters
  -> implements Domain/Application Ports
SQLite / External HTTP
```

- 领域层不导入 FastAPI、SQLAlchemy、ECharts 或数据源 SDK。
- UI 只消费 API DTO，不读取数据库结构。
- 外部适配器只能返回来源模型，不直接写仓储。
- 日期映射、缓存缺口和重复提示保持在已定义职责中。

## 后端模块边界

| 模块 | 责任 | 拥有的端口 |
| --- | --- | --- |
| catalog | 研究对象和最后状态 | SecuritySearchPort、ResearchObjectRepository |
| market | 行情查询、校验、聚合和缓存 | MarketDataProvider、MarketSeriesRepository |
| discovery | 信息搜索会话和候选规范化 | InformationSearchProvider |
| events | 事件、分类、标签、关联和投影 | EventRepository、ObjectReferenceReader |
| shared | ID、日期范围、结构化问题、时钟 | 无业务实体 |
| api | 用例调用、DTO 转换和用户错误文本 | 不拥有领域规则 |

禁止建立 `utils` 作为混杂业务规则的容器。

## API 边界

一期使用本机 JSON API，建议路径如下；最终字段以基线和 OpenAPI 契约测试为准：

| 方法与路径 | 用例 |
| --- | --- |
| `GET /api/health` | 启动器健康检查 |
| `GET /api/securities/search?q=` | 搜索证券候选 |
| `GET/POST /api/research-objects` | 列出或创建对象 |
| `GET/DELETE /api/research-objects/{id}` | 打开或删除对象 |
| `PUT /api/research-objects/{id}/state` | 保存最后页面状态 |
| `GET /api/research-objects/{id}/bars` | 获取指定区间和周期 K 线 |
| `POST /api/research-objects/{id}/market-refresh` | 显式更新行情缺口 |
| `POST /api/information-searches` | 创建当前搜索会话首页 |
| `GET /api/information-searches/{id}/pages/{page}` | 加载下一页 |
| `POST /api/events/duplicate-assessment` | 保存前重复提示 |
| `GET/POST /api/events` | 查询或新增事件 |
| `PUT/DELETE /api/events/{id}` | 编辑或删除事件 |
| `GET /api/research-objects/{id}/chart-events` | 获取当前图表事件投影 |

搜索会话可以只保存在后端内存中；服务重启后会话 ID 失效，符合未确认结果不持久化规则。

## 数据所有权与关系

建议的持久化集合，不等同于领域模型：

- `research_objects`：稳定 ID、证券市场、代码、类型、名称。
- `research_states`：每对象一条最后页面状态。
- `daily_bars`：证券身份 + 日期唯一，保存 OHLCV 和来源标识。
- `market_coverages`：已成功缓存的连续或分段范围及更新时间。
- `events`：真实日期、标题、摘要、来源名称和链接。
- `event_research_objects`：事件与对象多对多关系。
- `categories`：预置基础分类，使用稳定 ID。
- `tags` 与 `event_tags`：自定义标签和关联。

事务边界：

- 创建/修改事件与其全部关联在一个事务中提交。
- 删除研究对象与解除关联在一个事务中提交。
- 一个来源批次的合法行情与覆盖元数据在一个事务中提交。

## 缓存策略

- SQLite 中的 `daily_bars` 就是持久行情缓存，不额外引入 Redis 或文件缓存层。
- 请求时根据实际日线日期和 coverage 元数据计算缺口；coverage 只能作为优化，不能代替日线事实检查。
- 当用户请求延伸至最新日期时，最后一个缓存交易日之后的范围允许重新查询。
- 周/月 K 和事件投影在进程内按请求计算；可做短生命周期内存缓存，但其键必须包含对象、范围、周期、筛选及底层数据版本。
- 事件或日线提交后使相关投影内存缓存失效。

## 并发、取消与幂等

- 前端为每个研究页面使用请求序号或取消令牌，只接受最新请求响应。
- 后端对同一证券的重叠行情更新使用进程内细粒度锁；不同证券可以并行获取。
- SQLite 写事务保持短小；配置 busy timeout，避免浏览器读请求因瞬时写入失败。
- 日线以证券+日期唯一键保证幂等；事件新增使用一次性客户端请求 ID 防止双击重复保存，但不把相似事件自动视为相同。
- 搜索分页以会话 ID、页号和候选指纹去重。

## 外部请求与降级

- 所有 HTTP 适配器设置连接和读取超时、有限响应大小、明确 User-Agent，并校验内容类型。
- 行情：主源失败后尝试该证券类型已配置的备用源；全部失败返回缓存实际范围和问题。
- 信息搜索：失败只影响当前搜索，不影响图表和事件；手工补录始终可用。
- 外部响应视为不可信：标题、摘要和链接进行长度限制和转义；不执行返回 HTML 或脚本。
- 一期不绕过验证码、不登录网站、不抓取付费内容。

## 页面结构

### 首页

- 顶部证券搜索框和候选列表。
- 已有研究对象卡片或紧凑列表。
- 删除对象有明确确认。

### 研究页面

- 顶部：对象身份、日期范围、日/周/月切换、行情刷新。
- 主区：ECharts K 线 + 成交量 + 简短事件聚合标记。
- 工具区：事件分类和标签筛选、搜索信息、手工补录。
- 图下：按日期倒序的事件详情列表，与图表双向定位。
- 搜索结果和事件编辑使用页面内面板或对话框；不压缩 K 线为永久侧栏布局。

## 配置与本地目录

- 应用数据位于用户本地应用数据目录的固定产品子目录，不保存在安装目录或当前工作目录。
- 包含数据库、日志、版本和非敏感配置；不保存凭据。
- 数据源超时、主备顺序和本机端口范围为应用配置，采用安全默认值。
- 发布版前端资源与可执行文件只读，用户数据目录可写。

## 启动、升级和恢复

- 启动器检测是否已有实例；已有实例则只打开浏览器，不重复启动写入进程。
- 数据库迁移在服务接受请求前执行；迁移失败则停止启动并保留原文件。
- 每次结构迁移前创建一致性数据库备份；WAL 模式下通过数据库备份 API 或停写 checkpoint 完成，不直接复制活动主文件。
- 一期不提供 UI 备份导出，但内部升级备份属于可靠性措施，不违背范围。
- 应用异常退出后由 SQLite 日志恢复；下次启动执行完整性快速检查。

## 可观测性

- 本地滚动日志，记录启动、迁移、外部请求来源/耗时/状态、缓存命中、结构化问题和未处理异常。
- 不记录完整网页内容，不记录未来可能出现的敏感查询参数。
- API 返回关联请求 ID；用户错误只显示简明原因和重试建议，日志保留技术原因。
- 健康接口报告应用版本、数据库可用性和迁移版本，不暴露本地路径。

## 测试策略

- 领域单元测试：日期映射、周期聚合、缺口计算、OHLCV 校验、重复提示、对象唯一性和删除规则。
- 适配器契约测试：为每个免费数据源保存小型响应样本，并安排可显式运行的在线烟雾测试；接口变化时只修改适配器。
- 仓储集成测试：SQLite 临时库、事务回滚、唯一约束、迁移和异常恢复。
- API 契约测试：基线 JSON 对应的主流程和结构化问题。
- 前端组件测试：筛选、聚合标记、点击双向定位、搜索分页和编辑确认。
- 端到端测试：创建对象、查看 K 线、搜索确认、手工补录、重启恢复和删除对象不删事件。
- 性能测试：10 年日线 + 5,000 事件，在目标 Windows 环境缓存命中后测量 API、投影及首屏总耗时。

## 需求与架构追踪

| 需求区域 | 上下文/职责 | 架构决定 |
| --- | --- | --- |
| 研究对象唯一性 | CTX-CATALOG / RESP-OBJECT | ADR-002、003、005 |
| 行情主备与缓存 | CTX-MARKET / RESP-MARKET | ADR-002、005、006 |
| 日周月 K 与交互 | RESP-PERIOD / RESP-PRESENT | ADR-003、004 |
| 信息搜索与临时候选 | CTX-DISCOVERY / RESP-SEARCH | ADR-002、006 |
| 事件确认与多对象关联 | CTX-EVENT / RESP-CAPTURE | ADR-005 |
| 日期映射与聚合 | RESP-PROJECTION | ADR-002、004 |
| Windows 双击启动 | 应用生命周期 | ADR-001、007 |

## 安全网审查

- 每个运行组件只有一个主要责任，依赖指向领域合同。
- 外部源、UI 和存储均可替换而不改变日期映射或事件规则。
- 没有可选组件失败会破坏已确认事件；信息搜索失败有手工补录兜底。
- 所有写入一致性边界均有本地事务。
- 单进程和 SQLite 容量远高于一期量化负载，无中间件缺口。
- 启动、迁移、缓存冲突、外部源失败和异常退出均有恢复路径。
