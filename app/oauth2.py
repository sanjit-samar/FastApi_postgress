from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from . import schemas, model, database
from sqlalchemy.orm import Session
import jwt

# If the token is return as bearer token, to set in session or local the to use OauthpasswordBearer
# Not for cookies
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    # Make a copy so we don't modify the original dictionary
    to_encode = data.copy()

    # Create expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add expiration to payload
    to_encode.update({"exp": expire})

    # Generate JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)

        return token_data

    except jwt.PyJWTError:
        raise credentials_exception


# def get_current_user(token: str = Depends(oauth_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="User is not Valid",
#         headers={"www-Authenticate": "Bearer"},
#     )
#     return verify_access_token(token, credentials_exception)


def get_current_user(
    token: str = Depends(oauth_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    user = db.query(model.User).filter(model.User.id == token_data.id).first()

    if user is None:
        raise credentials_exception

    return user
