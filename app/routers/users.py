from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                authenticated_user: int = Depends(oauth2.get_current_user)):
    print(authenticated_user)
    # Hash password
    hashed_password = utils.hasher(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{id}', response_model=schemas.UserResponse)
def get_users(id: int, db: Session = Depends(get_db), authenticated_user: int = Depends(oauth2.get_current_user)):
    print(authenticated_user)
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {id} does not exist')
    return user
