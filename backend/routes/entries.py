import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db, SessionLocal, Entry, Setting, Todo
from backend.models import EntryCreate, EntryResponse
from backend.services import agent

router = APIRouter()


def _str_list(raw: str) -> list:
    items = json.loads(raw or "[]")
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, str)]


def _entry_to_dict(e: Entry) -> dict:
    return {
        "id": e.id,
        "version": e.version or "",
        "raw_text": e.raw_text or "",
        "summary": str(e.summary or ""),
        "tags": _str_list(e.tags),
        "changelog": _str_list(e.changelog),
        "key_ideas": _str_list(e.key_ideas),
        "open_questions": _str_list(e.open_questions),
        "action_items": _str_list(e.action_items),
        "drift_score": e.drift_score or 50,
        "connections": _str_list(e.connections),
        "created_at": e.created_at.isoformat(),
    }


def _next_version(last_version: str | None) -> str:
    if not last_version:
        return "v0.0.1"
    parts = last_version.lstrip("v").split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return "v" + ".".join(parts)


@router.post("/entry", response_model=EntryResponse)
def create_entry(payload: EntryCreate, db: Session = Depends(get_db)):
    last_entries = (
        db.query(Entry).order_by(Entry.created_at.desc()).limit(7).all()
    )
    last_version = last_entries[0].version if last_entries else None

    focus_setting = db.query(Setting).filter(Setting.key == "weekly_focus").first()
    weekly_focus = focus_setting.value if focus_setting else "no specific focus set"

    context = [_entry_to_dict(e) for e in reversed(last_entries)]

    try:
        structured = agent.structure_entry(payload.raw_text, weekly_focus, context)
    except (json.JSONDecodeError, Exception) as exc:
        raise HTTPException(status_code=502, detail=f"Claude error: {exc}")

    new_entry = Entry(
        version=_next_version(last_version),
        raw_text=payload.raw_text,
        summary=structured["summary"],
        tags=json.dumps(structured.get("tags", [])),
        changelog=json.dumps(structured.get("changelog", [])),
        key_ideas=json.dumps(structured.get("key_ideas", [])),
        open_questions=json.dumps(structured.get("open_questions", [])),
        action_items=json.dumps(structured.get("action_items", [])),
        drift_score=int(structured.get("drift_score", 50)),
        connections=json.dumps(structured.get("connections", [])),
        created_at=datetime.utcnow(),
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return EntryResponse(**_entry_to_dict(new_entry))


@router.post("/entry/stream")
def stream_entry(payload: EntryCreate):
    db = SessionLocal()
    try:
        last_entries = db.query(Entry).order_by(Entry.created_at.desc()).limit(7).all()
        last_version = last_entries[0].version if last_entries else None
        focus_setting = db.query(Setting).filter(Setting.key == "weekly_focus").first()
        weekly_focus = focus_setting.value if focus_setting else "no specific focus set"
        context = [_entry_to_dict(e) for e in reversed(last_entries)]
    finally:
        db.close()

    def generate():
        db = SessionLocal()
        try:
            structured = None
            for token, result in agent.structure_entry_stream(payload.raw_text, weekly_focus, context):
                if token is not None:
                    yield f"data: {json.dumps({'t': token})}\n\n"
                else:
                    structured = result

            if structured is None:
                yield f"data: {json.dumps({'error': 'empty response'})}\n\n"
                return

            new_entry = Entry(
                version=_next_version(last_version),
                raw_text=payload.raw_text,
                summary=structured["summary"],
                tags=json.dumps(structured.get("tags", [])),
                changelog=json.dumps(structured.get("changelog", [])),
                key_ideas=json.dumps(structured.get("key_ideas", [])),
                open_questions=json.dumps(structured.get("open_questions", [])),
                action_items=json.dumps(structured.get("action_items", [])),
                drift_score=int(structured.get("drift_score", 50)),
                connections=json.dumps(structured.get("connections", [])),
                created_at=datetime.utcnow(),
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)

            for item in structured.get("action_items", []):
                if isinstance(item, str) and item.strip():
                    db.add(Todo(entry_id=new_entry.id, entry_version=new_entry.version, text=item))
            db.commit()

            yield f"data: {json.dumps({'done': True, 'entry': _entry_to_dict(new_entry)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            db.close()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/entries")
def get_entries(db: Session = Depends(get_db)):
    entries = db.query(Entry).order_by(Entry.created_at.desc()).all()
    return [_entry_to_dict(e) for e in entries]
