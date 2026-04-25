import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db, Todo

router = APIRouter()


class TodoResponse(BaseModel):
    id: int
    entry_id: int
    entry_version: str
    text: str
    completed: bool

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    entry_id: int
    entry_version: str
    text: str


class TodoToggle(BaseModel):
    completed: bool


@router.post("/todos", response_model=TodoResponse)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(entry_id=payload.entry_id, entry_version=payload.entry_version, text=payload.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).order_by(Todo.entry_id.desc(), Todo.id).all()


@router.patch("/todos/{todo_id}", response_model=TodoResponse)
def toggle_todo(todo_id: int, payload: TodoToggle, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = payload.completed
    db.commit()
    db.refresh(todo)
    return todo
