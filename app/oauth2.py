from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
import logging

from sqlalchemy.orm import Session
from typing import Annotated
from jose import jwt, JWTError
from datetime import datetime, timedelta
import pytz

from . import schemas, database, models, utils
from .config import settings





# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

class OAuth2PasswordCookie(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl=tokenUrl)

    def __call__(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                          detail="Redirecting to Login...",
                                          headers={"Location":"/users/login"})
            #raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return token

oauth2_scheme = OAuth2PasswordCookie(tokenUrl="token")



SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes





def create_access_token(data: dict):
    to_encode = data.copy()
    #expire session 30 mins from now
    
    expire = datetime.now(pytz.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt






def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        user_id = payload.get("user_id") #user_id
        # logger.debug(f"Deoded payload: {payload}")

        if user_id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=str(user_id))
        # logger.debug(f"Token data: {token_data}") #DEBUG
    except JWTError as e:
        # logger.debug(f"Error al decodificar el token: {str(e)}") #DEBUG
        raise credentials_exception
    return token_data




async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                          detail="Redirecting to Login...",
                                          headers={"Location":"/users/login"})
    #print(f"received token: {token}")
    token_data = verify_access_token(token, credentials_exception)
    
    #print(f"Token data: {token_data}")
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    #print(f"User found: {user}")

    if user:
        print(f"autenticado el usuario: {user.email}")
    else:
        print("no autenticado")
        raise credentials_exception
    
    return user


async def get_optional_user(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None 



