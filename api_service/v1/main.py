from typing import List

from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

import database

from . import models, schemas

app = FastAPI(
    title="API Version 1",
    description="This is the first version of our API.",
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc",
)


@app.get("/todos/", response_model=List[schemas.TodoSchema], tags=["Todos"])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieve all Todo items from the shared database.
    """
    todos = db.query(models.Todo).offset(skip).limit(limit).all()
    return todos


@app.post("/todos/", response_model=schemas.TodoSchema, status_code=status.HTTP_201_CREATED, tags=["Todos"])
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(database.get_db)):
    """
    Create a new Todo item in the database.
    """
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
