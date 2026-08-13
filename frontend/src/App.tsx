import { useEffect, useState } from "react";

import "./styles.css";

type ResearchObject = {
  id: string;
  market: string;
  code: string;
  name: string;
  type: string;
};

type EventRecord = {
  id: string;
  publishedOn: string;
  title: string;
  summary: string | null;
  sourceName: string | null;
  sourceUrl: string | null;
  categoryId: string | null;
  tags: string[];
  linkedResearchObjectIds: string[];
};

export default function App() {
  const [objects, setObjects] = useState<ResearchObject[]>([]);
  const [selected, setSelected] = useState<ResearchObject | null>(null);
  const [events, setEvents] = useState<EventRecord[]>([]);

  useEffect(() => {
    void fetch("/api/research-objects")
      .then((response) => response.json() as Promise<ResearchObject[]>)
      .then(setObjects);
  }, []);

  async function openResearch(researchObject: ResearchObject) {
    setSelected(researchObject);
    const response = await fetch(`/api/events?researchObjectId=${researchObject.id}`);
    setEvents((await response.json()) as EventRecord[]);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">本地投研工作台</span>
          <strong>行情与事件研究</strong>
        </div>
        <button className="primary-action" type="button">新增研究对象</button>
      </header>

      <div className="workspace">
        <aside className="catalog">
          <h2>研究对象</h2>
          {objects.length === 0 ? <p className="muted">暂无研究对象</p> : null}
          <nav aria-label="研究对象列表">
            {objects.map((item) => (
              <button
                className={selected?.id === item.id ? "object-card active" : "object-card"}
                key={item.id}
                onClick={() => void openResearch(item)}
                type="button"
              >
                <span>{item.name}</span>
                <small>{item.code} · {item.type}</small>
              </button>
            ))}
          </nav>
        </aside>

        <main className="research-page">
          {selected ? (
            <>
              <section className="research-heading">
                <div>
                  <span className="eyebrow">{selected.code}</span>
                  <h1>{selected.name}</h1>
                </div>
                <div className="period-switch" aria-label="K 线周期">
                  <button className="selected" type="button">日 K</button>
                  <button type="button">周 K</button>
                  <button type="button">月 K</button>
                </div>
              </section>

              <section className="chart-panel" aria-label="K 线图区域">
                <div className="chart-placeholder">
                  <span>K 线图将在行情模块接入后显示</span>
                </div>
              </section>

              <section className="event-section">
                <div className="section-title">
                  <div>
                    <span className="eyebrow">时间轴</span>
                    <h2>关键事件</h2>
                  </div>
                  <button className="primary-action" type="button">手工补录</button>
                </div>
                {events.length === 0 ? <p className="empty-state">当前对象还没有事件。</p> : null}
                <div className="event-list">
                  {events.map((event) => (
                    <article className="event-card" key={event.id}>
                      <time>{event.publishedOn}</time>
                      <div>
                        <h3>{event.title}</h3>
                        {event.summary ? <p>{event.summary}</p> : null}
                        <div className="event-meta">
                          <span>{event.sourceName ?? "来源未记录"}</span>
                          {event.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}
                          {event.sourceUrl ? <a href={event.sourceUrl} rel="noreferrer" target="_blank">查看来源</a> : null}
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </>
          ) : (
            <section className="welcome">
              <span className="eyebrow">开始研究</span>
              <h1>选择一个研究对象</h1>
              <p>行情、事件标记和完整信息会集中展示在同一个研究页面。</p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
