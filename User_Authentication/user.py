from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from Database_connection import sessionlocal
from model import TransactionTable, UserTable
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt

router = APIRouter()

def database_open():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(database_open)]
SECRET_KEY = '172b27c7aed255f1378fa10f0eee8da144de4bd41f4b1a6437244aa9117b5711'
ALGORITHM ='HS256'

#------------------JWT-Token-Create-------------------#
def create_token(username: str, user_id: int, expire: timedelta):
    encode = {'sub': username, 'id': user_id}
    expire_time = datetime.now(timezone.utc) + expire
    encode.update({'exp':expire_time})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

#---------------JWT-Token-Decode-------------------#
oth_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')
def decode_token(token: Annotated[str, Depends(oth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            return JSONResponse(status_code=404, content='User Not Found')
        else:
            return({'username': username, 'id': user_id})
    except:
        return JSONResponse(status_code=404, content='User Not Found')
    
#-------------------Hashpass----------------------#
bcrypt_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

#----------------------User Registation-------------------------#
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password : str = Field(min_length=6, max_length=50)

@router.post('/auth/register')
def User_Registation(db: db_dependency, new_user: UserCreate):
    user_new = UserTable(
        username = new_user.username,
        email = new_user.email,
        password = bcrypt_context.hash(new_user.password)
    )
    db.add(user_new)
    db.commit()
    return JSONResponse(status_code=201, content='User registered successfully')

#-------------User-Login--------------------#
def user_login_matching(username, password, db):
    user = db.query(UserTable).filter(UserTable.username == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password, user.password):
        return user
    return False

@router.post('/auth/login')
def User_Login(db: db_dependency, from_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_matching = user_login_matching(from_data.username, from_data.password, db)
    if not user_matching:
        raise HTTPException(status_code=401, detail='Incorrect Password')
    
    token = create_token(user_matching.username, user_matching.id, timedelta(minutes=30))
    return { "access_token": token, "token_type": "bearer"}