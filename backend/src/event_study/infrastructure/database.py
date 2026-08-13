from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


event_research_objects = Table(
    "event_research_objects",
    Base.metadata,
    Column("event_id", ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "research_object_id",
        ForeignKey("research_objects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ResearchObjectRecord(Base):
    __tablename__ = "research_objects"
    __table_args__ = (UniqueConstraint("market", "code", "type"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    market: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    events: Mapped[list["EventRecord"]] = relationship(
        secondary=event_research_objects,
        back_populates="research_objects",
    )


class EventRecord(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    published_on: Mapped[object] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[str | None] = mapped_column(String)
    tags_text: Mapped[str] = mapped_column(Text, default="")
    research_objects: Mapped[list[ResearchObjectRecord]] = relationship(
        secondary=event_research_objects,
        back_populates="events",
    )


def create_session_factory(database_url: str) -> sessionmaker:
    engine = create_engine(database_url)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
