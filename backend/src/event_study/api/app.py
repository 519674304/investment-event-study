from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from event_study.infrastructure.database import (
    EventRecord,
    ResearchObjectRecord,
    create_session_factory,
)


APPLICATION_VERSION = "0.1.0"
SCHEMA_VERSION = "0001"


class ResearchObjectInput(BaseModel):
    market: str
    code: str
    name: str
    type: str


class ResearchObjectOutput(ResearchObjectInput):
    model_config = ConfigDict(from_attributes=True)
    id: str


class EventInput(BaseModel):
    publishedOn: date
    title: str
    summary: str | None = None
    sourceName: str | None = None
    sourceUrl: str | None = None
    categoryId: str | None = None
    tags: list[str] = Field(default_factory=list)
    linkedResearchObjectIds: list[str]


class EventOutput(EventInput):
    id: str


def event_output(record: EventRecord) -> EventOutput:
    return EventOutput(
        id=record.id,
        publishedOn=record.published_on,
        title=record.title,
        summary=record.summary,
        sourceName=record.source_name,
        sourceUrl=record.source_url,
        categoryId=record.category_id,
        tags=[tag for tag in record.tags_text.split("\n") if tag],
        linkedResearchObjectIds=sorted(item.id for item in record.research_objects),
    )


def create_app(database_url: str | None = None) -> FastAPI:
    if database_url is None:
        data_dir = Path.home() / "AppData" / "Local" / "InvestmentEventStudy"
        data_dir.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{data_dir / 'event-study.db'}"
    sessions = create_session_factory(database_url)
    app = FastAPI(title="Investment Event Study", version=APPLICATION_VERSION)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "applicationVersion": APPLICATION_VERSION,
            "schemaVersion": SCHEMA_VERSION,
        }

    @app.post("/api/research-objects", response_model=ResearchObjectOutput)
    def create_research_object(payload: ResearchObjectInput, response: Response):
        with sessions.begin() as session:
            existing = session.scalar(
                select(ResearchObjectRecord).where(
                    ResearchObjectRecord.market == payload.market,
                    ResearchObjectRecord.code == payload.code,
                    ResearchObjectRecord.type == payload.type,
                )
            )
            if existing is not None:
                response.status_code = status.HTTP_200_OK
                return existing
            record = ResearchObjectRecord(id=str(uuid4()), **payload.model_dump())
            session.add(record)
            session.flush()
            response.status_code = status.HTTP_201_CREATED
            return record

    @app.get("/api/research-objects", response_model=list[ResearchObjectOutput])
    def list_research_objects() -> list[ResearchObjectRecord]:
        with sessions() as session:
            return list(session.scalars(select(ResearchObjectRecord).order_by(ResearchObjectRecord.name)))

    @app.delete("/api/research-objects/{object_id}", status_code=204)
    def delete_research_object(object_id: str) -> None:
        with sessions.begin() as session:
            record = session.get(ResearchObjectRecord, object_id)
            if record is None:
                raise HTTPException(status_code=404, detail="Research object not found")
            session.delete(record)

    @app.post("/api/events", response_model=EventOutput, status_code=201)
    def create_event(payload: EventInput) -> EventOutput:
        with sessions.begin() as session:
            objects = list(
                session.scalars(
                    select(ResearchObjectRecord).where(
                        ResearchObjectRecord.id.in_(payload.linkedResearchObjectIds)
                    )
                )
            )
            if len(objects) != len(set(payload.linkedResearchObjectIds)):
                raise HTTPException(status_code=422, detail="Unknown research object")
            record = EventRecord(
                id=str(uuid4()),
                published_on=payload.publishedOn,
                title=payload.title,
                summary=payload.summary,
                source_name=payload.sourceName,
                source_url=payload.sourceUrl,
                category_id=payload.categoryId,
                tags_text="\n".join(payload.tags),
                research_objects=objects,
            )
            session.add(record)
            session.flush()
            return event_output(record)

    @app.get("/api/events", response_model=list[EventOutput])
    def list_events(researchObjectId: str | None = None) -> list[EventOutput]:
        with sessions() as session:
            query = select(EventRecord)
            if researchObjectId is not None:
                query = query.where(EventRecord.research_objects.any(id=researchObjectId))
            records = session.scalars(
                query.order_by(EventRecord.published_on.desc(), EventRecord.id)
            ).all()
            return [event_output(record) for record in records]

    @app.get("/api/events/{event_id}", response_model=EventOutput)
    def get_event(event_id: str) -> EventOutput:
        with sessions() as session:
            record = session.get(EventRecord, event_id)
            if record is None:
                raise HTTPException(status_code=404, detail="Event not found")
            return event_output(record)

    @app.put("/api/events/{event_id}", response_model=EventOutput)
    def update_event(event_id: str, payload: EventInput) -> EventOutput:
        with sessions.begin() as session:
            record = session.get(EventRecord, event_id)
            if record is None:
                raise HTTPException(status_code=404, detail="Event not found")
            objects = list(
                session.scalars(
                    select(ResearchObjectRecord).where(
                        ResearchObjectRecord.id.in_(payload.linkedResearchObjectIds)
                    )
                )
            )
            if len(objects) != len(set(payload.linkedResearchObjectIds)):
                raise HTTPException(status_code=422, detail="Unknown research object")
            record.published_on = payload.publishedOn
            record.title = payload.title
            record.summary = payload.summary
            record.source_name = payload.sourceName
            record.source_url = payload.sourceUrl
            record.category_id = payload.categoryId
            record.tags_text = "\n".join(payload.tags)
            record.research_objects = objects
            session.flush()
            return event_output(record)

    @app.delete("/api/events/{event_id}", status_code=204)
    def delete_event(event_id: str) -> None:
        with sessions.begin() as session:
            record = session.get(EventRecord, event_id)
            if record is None:
                raise HTTPException(status_code=404, detail="Event not found")
            session.delete(record)

    return app
