from typing import List
from fastapi import Response, status, HTTPException, APIRouter

from app import oauth2
from .. import model, schemas
from sqlalchemy.orm import Session
from ..database import engine, Base, get_db
from fastapi import Depends

Base.metadata.create_all(bind=engine)
router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    posts = db.query(model.Post).filter(model.Post.owner_id == current_user.id).all()

    return posts


@router.get("/{id}")
def get_post(
    id: int,
    db: Session = Depends(get_db),
    get_current_user=Depends(oauth2.get_current_user),
):
    """Get a single post by ID"""
    post = db.query(model.Post).filter(model.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    return post


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    get_current_user=Depends(oauth2.get_current_user),
):
    """Create a new post"""
    new_post = model.Post(owner_id=get_current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/{id}")
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    get_current_user=Depends(oauth2.get_current_user),
):
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    get_current_user=Depends(oauth2.get_current_user),
):
    """Delete a post by ID"""

    delete_post = db.query(model.Post).filter(model.Post.id == id)
    post = delete_post.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    if post.owner_id != get_current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    delete_post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
