from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
