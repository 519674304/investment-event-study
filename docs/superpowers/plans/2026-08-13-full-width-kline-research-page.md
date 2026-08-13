# Full-Width K-Line Research Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved full-width research page with real cached daily K-line data, day/week/month aggregation, K-line event markers, and bidirectional navigation between chart markers and event details.

**Architecture:** Keep provider-specific HTTP parsing behind `MarketDataProvider`, validate and persist canonical daily bars in SQLite, and derive week/month bars without refetching. The frontend consumes one chart-view API, renders ECharts candlesticks and volume, and keeps full event content below the chart while chart markers contain only short labels.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2, SQLite, pytest, React 19, TypeScript, Vite, Vitest, Apache ECharts.

## Global Constraints

- Scope is A-share stocks, A-share industry indices, and concept indices.
- Market requests occur only after the user selects an object and date range.
- A cached interval is not fetched twice; only missing intervals are requested.
- A non-trading-day event maps to the preceding available bar while preserving its real publication date.
- Chart output must not infer leading, lagging, bullish, or bearish meaning.
- The page uses the approved full-width layout; complete event content stays below the chart.
- All production behavior follows red-green-refactor TDD.

---

### Task 1: Canonical market-bar domain and period aggregation

**Files:**
- Create: `backend/src/event_study/market/domain.py`
- Create: `backend/tests/test_market_domain.py`

**Interfaces:**
- Produces: `MarketBar`, `validate_bars(bars)`, and `aggregate_bars(bars, period)` where `period` is `day`, `week`, or `month`.
- Consumers: Tasks 2, 3, and 5.

- [ ] **Step 1: Write failing tests for OHLC validation, chronological uniqueness, and week/month aggregation**

```python
def test_rejects_high_below_close():
    with pytest.raises(ValueError, match="high"):
        validate_bars([MarketBar(date(2026, 8, 10), 10, 10, 9, 11, 100)])

def test_aggregates_week_from_daily_bars():
    result = aggregate_bars(BARS, "week")
    assert result == [MarketBar(date(2026, 8, 7), 10, 13, 9, 12, 600)]
```

- [ ] **Step 2: Run `backend/.venv/Scripts/python.exe -m pytest -q backend/tests/test_market_domain.py` and confirm failures are caused by the missing domain module**
- [ ] **Step 3: Implement immutable decimal-safe bars, validation, and calendar week/month aggregation**
- [ ] **Step 4: Rerun the targeted test and the complete backend suite**
- [ ] **Step 5: Commit with `git commit -m "add validated market bar domain"`**

### Task 2: SQLite bar cache and missing-interval calculation

**Files:**
- Modify: `backend/src/event_study/infrastructure/database.py`
- Create: `backend/src/event_study/market/repository.py`
- Create: `backend/tests/test_market_repository.py`

**Interfaces:**
- Consumes: `MarketBar` from Task 1.
- Produces: `MarketBarRepository.load(object_id, start, end)`, `save(object_id, source, bars)`, and `missing_intervals(object_id, start, end)`.
- Consumers: Task 3.

- [ ] **Step 1: Write failing persistence tests for restart recovery, idempotent save, and interval gaps**

```python
def test_returns_only_uncached_leading_and_trailing_intervals(repository):
    repository.save("hog", "fixture", bars_for("2026-08-05", "2026-08-08"))
    assert repository.missing_intervals("hog", date(2026, 8, 1), date(2026, 8, 10)) == [
        DateInterval(date(2026, 8, 1), date(2026, 8, 4)),
        DateInterval(date(2026, 8, 9), date(2026, 8, 10)),
    ]
```

- [ ] **Step 2: Run the targeted test and confirm the repository is missing**
- [ ] **Step 3: Add the `market_bars` table with `(research_object_id, date)` uniqueness, source, and update timestamp; implement transactional upsert and range reads**
- [ ] **Step 4: Rerun targeted and complete backend tests**
- [ ] **Step 5: Commit with `git commit -m "persist incremental market bar cache"`**

### Task 3: Provider port, fixture provider, and chart-view API

**Files:**
- Create: `backend/src/event_study/market/provider.py`
- Create: `backend/src/event_study/market/service.py`
- Modify: `backend/src/event_study/api/app.py`
- Create: `backend/tests/test_market_api.py`
- Add fixtures: `backend/tests/fixtures/market/*.json`

**Interfaces:**
- Produces: `MarketDataProvider.fetch(research_object, start, end) -> ProviderResult` and `GET /api/research-objects/{id}/market-bars?start=YYYY-MM-DD&end=YYYY-MM-DD&period=day|week|month`.
- API response: `{bars, actualStart, actualEnd, dataCutoff, source, problems}`.
- Consumers: Tasks 4 and 5.

- [ ] **Step 1: Write a failing API test injecting a recording fixture provider and requesting the same interval twice**

```python
first = client.get(f"/api/research-objects/{object_id}/market-bars?start=2026-08-01&end=2026-08-10&period=day")
second = client.get(f"/api/research-objects/{object_id}/market-bars?start=2026-08-01&end=2026-08-10&period=week")
assert first.status_code == second.status_code == 200
assert provider.calls == [(date(2026, 8, 1), date(2026, 8, 10))]
```

- [ ] **Step 2: Run the targeted test and confirm the route/provider injection is missing**
- [ ] **Step 3: Implement provider injection, fetch-only-missing orchestration, validation-before-save, aggregation, and structured source/problem metadata**
- [ ] **Step 4: Rerun targeted and complete backend tests**
- [ ] **Step 5: Commit with `git commit -m "serve cached market chart data"`**

### Task 4: Convert the current shell to the approved full-width layout

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: existing research-object and event APIs.
- Produces: full-width page hierarchy with object picker, recent-object chips, chart controls, chart region, filters, and event details.
- Consumers: Tasks 5 and 6.

- [ ] **Step 1: Replace the current sidebar-oriented assertion with a failing layout test**

```tsx
expect(screen.getByRole("main")).toHaveClass("full-width-research");
expect(screen.getByLabelText("最近研究对象")).toBeAbove(screen.getByLabelText("K 线图区域"));
expect(screen.getByLabelText("K 线图区域")).toBeAbove(screen.getByRole("heading", { name: "关键事件" }));
```

- [ ] **Step 2: Run `pnpm test` and confirm it fails on the missing full-width hierarchy**
- [ ] **Step 3: Remove the permanent sidebar and implement the approved top controls → chart → filters → event details hierarchy**
- [ ] **Step 4: Rerun frontend tests and `pnpm build`**
- [ ] **Step 5: Commit with `git commit -m "adopt full-width research layout"`**

### Task 5: ECharts candlesticks, volume, periods, and request state

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/market/types.ts`
- Create: `frontend/src/market/api.ts`
- Create: `frontend/src/chart/KLineChart.tsx`
- Create: `frontend/src/chart/chartOptions.ts`
- Create: `frontend/src/chart/chartOptions.test.ts`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: Task 3 market-bars API and Task 4 chart region.
- Produces: `KLineChart({ bars, markers, selectedMarkerId, onMarkerClick })` and `buildChartOptions()`.
- Consumers: Task 6.

- [ ] **Step 1: Write failing pure-option tests for red-up/green-down candles, volume panel, tooltip fields, and data zoom**
- [ ] **Step 2: Run the targeted Vitest file and confirm option construction is missing**
- [ ] **Step 3: Add `echarts`, implement typed API loading with abort-on-new-request, and render candlestick plus volume series**
- [ ] **Step 4: Add date controls and day/week/month buttons; each change requests the selected period and reports actual data cutoff**
- [ ] **Step 5: Rerun frontend tests and production build**
- [ ] **Step 6: Commit with `git commit -m "render interactive k-line chart"`**

### Task 6: Event projection, aggregation markers, filtering, and bidirectional navigation

**Files:**
- Create: `backend/src/event_study/events/projection.py`
- Create: `backend/tests/test_event_projection.py`
- Create: `frontend/src/chart/eventMarkers.ts`
- Create: `frontend/src/chart/eventMarkers.test.ts`
- Modify: `frontend/src/chart/KLineChart.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Produces: `project_events(bar_dates, events) -> ProjectedEventGroup[]` and frontend `EventMarker` with `barDate`, `realDates`, `shortLabel`, and `eventIds`.
- Bidirectional behavior: marker click focuses and scrolls the first linked event; detail click zooms/highlights its marker.

- [ ] **Step 1: Write failing backend tests for trading-day, Sunday-to-Friday, pre-range, and same-bar aggregation behavior**
- [ ] **Step 2: Run the backend test and confirm projection is missing**
- [ ] **Step 3: Implement binary-search projection without interpretation fields**
- [ ] **Step 4: Write failing frontend tests for short labels, `3 条事件` aggregation, category/tag filters, and click callbacks**
- [ ] **Step 5: Implement ECharts scatter/markPoint markers, hover details, filters, scrolling, focus styles, and chart positioning**
- [ ] **Step 6: Run complete backend/frontend tests and frontend build**
- [ ] **Step 7: Commit with `git commit -m "link chart markers with event details"`**

### Task 7: Real provider probe and production adapter decision

**Files:**
- Create: `tools/provider_probe/probe.py`
- Create: `backend/tests/fixtures/providers/stock.json`
- Create: `backend/tests/fixtures/providers/industry-index.json`
- Create: `backend/tests/fixtures/providers/concept-index.json`
- Create: `docs/project/evidence/provider-probe.md`
- Create or modify: `backend/src/event_study/market/providers/*.py`

**Interfaces:**
- Consumes: `MarketDataProvider` from Task 3.
- Produces: exact provider routing for `stock`, `industry_index`, and `concept_index`, including explicit absence of fallback where applicable.

- [ ] **Step 1: Run online probes for `002714`, one A-share industry index, and `884275`; save raw response samples and record URLs, fields, date coverage, and failure modes**
- [ ] **Step 2: Write failing offline parser contract tests from the captured samples**
- [ ] **Step 3: Implement only adapters proven by the probe; do not substitute a similar index**
- [ ] **Step 4: Add ordered fallback tests and a manually invoked online smoke test**
- [ ] **Step 5: Run all offline tests; run the online smoke test separately and record date/time/result**
- [ ] **Step 6: Commit with `git commit -m "connect verified public market providers"`**

### Task 8: Integrated verification and visual approval artifact

**Files:**
- Create: `docs/project/evidence/full-width-chart-check.md`
- Create: `docs/project/evidence/screenshots/full-width-chart.png`

**Interfaces:**
- Consumes: Tasks 1-7.
- Produces: a visual checkpoint before information-search work begins.

- [ ] **Step 1: Seed one `884275` research object, at least 40 bars, one Sunday event, and three events mapped to the same bar**
- [ ] **Step 2: Start the local app and capture the full-width chart with visible markers and below-chart details**
- [ ] **Step 3: Verify day/week/month, marker-to-detail, detail-to-marker, filters, and reload persistence; record each result**
- [ ] **Step 4: Run complete backend tests, frontend tests, frontend build, and `git diff --check`**
- [ ] **Step 5: Present the screenshot to the user for the visual checkpoint; do not begin information-search implementation until it is accepted**
- [ ] **Step 6: Commit with `git commit -m "verify full-width event chart workflow"`**
