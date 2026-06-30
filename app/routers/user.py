from typing import List
from fastapi import status, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError
from .. import model, schemas, utils
from sqlalchemy.orm import Session
from ..database import engine, Base, get_db
from fastapi import Depends

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/users", tags=["Users"])


# Users Part
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user"""
    # Hash the password
    utils.hash_password(user)

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


@router.get("/{id}", response_model=List[schemas.User])
def get_user(id: str, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )

    return user
