from datetime import datetime, timedelta

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import schemas, database, models

oauth2scheme = OAuth2PasswordBearer(tokenUrl='login')


# Secret key
SECRET_KEY = '464231ed749e490cae1719b8f3cdcb41cfab4bc39c299b0097e2563a26ac99fb'

# Algorithm
ALGORITHM = 'HS256'

# Expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get('user_id')

        if id is None:
            raise credential_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credential_exception

    return token_data


def get_current_user(token: str = Depends(oauth2scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f'Could not validate credentials',
                                          headers={'WWW-Authenticate': 'Bearer'})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
