import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./dailydiff.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    summary = Column(String, nullable=False)
    tags = Column(Text, default="[]")
    changelog = Column(Text, default="[]")
    key_ideas = Column(Text, default="[]")
    open_questions = Column(Text, default="[]")
    action_items = Column(Text, default="[]")
    drift_score = Column(Integer, default=50)
    connections = Column(Text, default="[]")
    notion_page_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, nullable=False)
    entry_version = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    completed = Column(Boolean, default=False)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_if_empty(db)
    finally:
        db.close()


def _seed_if_empty(db):
    if db.query(Entry).count() > 0:
        return

    seeds = [
        Entry(
            version="v0.0.1",
            raw_text="Read a bunch about system design today. CAP theorem is clicking now — consistency vs availability tradeoff. Bookmarked some papers. Didn't ship anything, just learning mode.",
            summary="Deep dive into system design fundamentals, CAP theorem finally clicked.",
            tags=json.dumps(["learning", "thinking"]),
            changelog=json.dumps([
                "Read through CAP theorem and distributed systems notes",
                "Bookmarked 3 papers on consistency models",
                "Set up a reading list for the week",
            ]),
            key_ideas=json.dumps([
                "CAP theorem: you can only guarantee 2 of 3 — consistency, availability, partition tolerance",
                "Most real systems choose AP or CP, rarely CA in distributed settings",
            ]),
            open_questions=json.dumps([
                "How does Cassandra handle eventual consistency in practice?",
                "When does strong consistency actually matter vs hurt performance?",
            ]),
            action_items=json.dumps(["Re-read the Dynamo paper this week"]),
            drift_score=72,
            connections=json.dumps([]),
            created_at=datetime(2026, 4, 22, 9, 30),
        ),
        Entry(
            version="v0.0.2",
            raw_text="Shipped a small prototype today. Fixed two bugs that were blocking progress — one in the data layer, one in the API response format. Feeling good. A bit tired but productive.",
            summary="Shipped prototype, fixed two blocking bugs, momentum feels good.",
            tags=json.dumps(["building"]),
            changelog=json.dumps([
                "Shipped v1 prototype with core read/write flow",
                "Fixed data layer bug causing duplicate records",
                "Fixed API response format mismatch on /entries endpoint",
            ]),
            key_ideas=json.dumps([
                "Shipping something rough and real beats waiting for perfect",
            ]),
            open_questions=json.dumps([
                "Should the API be paginated now or wait until it matters?",
            ]),
            action_items=json.dumps([
                "Write a quick test for the data layer fix",
                "Demo to a friend and get early feedback",
            ]),
            drift_score=88,
            connections=json.dumps([]),
            created_at=datetime(2026, 4, 23, 11, 0),
        ),
        Entry(
            version="v0.0.3",
            raw_text="Stuck today. Can't decide between two architecture approaches — go with a simple monolith now or design for services from the start. Spent too long going in circles. Need to just pick one.",
            summary="Blocked on architecture decision, spent the day in analysis paralysis.",
            tags=json.dumps(["blocked", "thinking"]),
            changelog=json.dumps([
                "Mapped out monolith vs services tradeoffs",
                "Drafted two rough architecture diagrams",
                "Decided to sleep on it — no decision made",
            ]),
            key_ideas=json.dumps([
                "Analysis paralysis is a real cost — time spent deciding is time not building",
            ]),
            open_questions=json.dumps([
                "What's the actual expected scale in 6 months?",
                "Can I defer the services decision until I have more data?",
            ]),
            action_items=json.dumps([
                "Set a 24hr deadline — commit to monolith and revisit at v1",
            ]),
            drift_score=31,
            connections=json.dumps(["v0.0.1: Both days circling system design — same domain, different layer"]),
            created_at=datetime(2026, 4, 24, 10, 0),
        ),
    ]

    for entry in seeds:
        db.add(entry)
    db.commit()
