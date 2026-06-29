from typing import List
from fastapi import FastAPI, Response, status, HTTPException
from sqlalchemy.exc import IntegrityError
from . import model, schemas
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from fastapi import Depends

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Blog API"}


@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    """Get all posts"""
    posts = db.query(model.Post).all()
    return posts


@app.get("/posts/{id}")
def get_post(
    id: int,
    db: Session = Depends(get_db),
):
    """Get a single post by ID"""
    post = db.query(model.Post).filter(model.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    new_post = model.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Update a post by ID"""
    post_updated = db.query(model.Post).filter(model.Post.id == id)

    if post_updated.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    post_updated.update(post.model_dump(), synchronize_session=False)
    db.commit()

    updated_post = post_updated.first()
    return updated_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    """Delete a post by ID"""
    delete_post = db.query(model.Post).filter(model.Post.id == id)
    if delete_post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    delete_post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Users Part
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user"""
    # Hash the password
    user.password = password_hash.hash(user.password)

    new_user = model.User(**user.model_dump())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    return new_user
