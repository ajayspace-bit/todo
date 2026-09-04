from fastapi import FastAPI , Depends
from schemas import Todo as TodoSchema , TodoCreate
from sqlalchemy.orm import Session
from database import sessionlocal, Base, engine
from models import Todo
from fastapi import HTTPException


Base.metadata.create_all(bind=engine)


app = FastAPI()

#dependency for database session

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

# post - Create a new todo

@app.post("/todos", response_model=TodoSchema)
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# get - all todos

@app.get("/todos", response_model = list[TodoSchema])
def read_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

# get - single todo
@app.get("/todos/{todo_id}", response_model=TodoSchema)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.id == todo_id).first()

#put - update a todo
@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    #update the todo
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.completed = todo.completed

    db.commit()
    db.refresh(db_todo)

    return db_todo

#update - partial update a todo
@app.patch("/todos/{todo_id}", response_model=TodoSchema)
def update_todo_partial(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    #update the todo
    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    if todo.completed is not None:
        db_todo.completed = todo.completed

    db.commit()
    db.refresh(db_todo)

    return db_todo

#delete - delete a todo
@app.delete("/todos/{todo_id}", response_model=TodoSchema)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()

    return db_todo



