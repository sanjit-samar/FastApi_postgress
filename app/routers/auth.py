from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from .. import database, model, schemas, utils, oauth2

router = APIRouter(tags=["login"])


@router.post("/login")
def login_user(
    user_Credentials: schemas.UserLogin, db: Session = Depends(database.get_db)
):
    user = (
        db.query(model.User).filter(model.User.email == user_Credentials.email).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{user_Credentials.email} is not valid",
        )
    if not utils.verify_password(user_Credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User is not valid"
        )
    # create a token if user is valid
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
