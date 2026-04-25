import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, Entry, Setting
from backend.models import WeeklySummaryResponse, SettingUpdate, SettingResponse
from backend.services import agent

router = APIRouter()


@router.get("/weekly-summary", response_model=WeeklySummaryResponse)
def get_weekly_summary(db: Session = Depends(get_db)):
    week_start = datetime.utcnow() - timedelta(days=7)
    entries = (
        db.query(Entry)
        .filter(Entry.created_at >= week_start)
        .order_by(Entry.created_at.asc())
        .all()
    )

    if not entries:
        raise HTTPException(status_code=404, detail="No entries this week")

    entries_data = [
        {
            "version": e.version,
            "summary": e.summary,
            "tags": json.loads(e.tags),
            "changelog": json.loads(e.changelog),
            "drift_score": e.drift_score,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]

    try:
        result = agent.generate_weekly_summary(entries_data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Claude error: {exc}")

    return WeeklySummaryResponse(**result)


@router.put("/settings/weekly-focus")
def set_weekly_focus(payload: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(Setting).filter(Setting.key == "weekly_focus").first()
    if setting:
        setting.value = payload.value
    else:
        db.add(Setting(key="weekly_focus", value=payload.value))
    db.commit()
    return {"ok": True}


@router.get("/settings/weekly-focus", response_model=SettingResponse)
def get_weekly_focus(db: Session = Depends(get_db)):
    setting = db.query(Setting).filter(Setting.key == "weekly_focus").first()
    return SettingResponse(value=setting.value if setting else "")
