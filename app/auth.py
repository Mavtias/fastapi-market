import logging
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from . import database, schemas, models, utils, oauth2

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/users", 
    tags=["Auth"]
    )
 
@router.post("/login", response_model = schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):
    #logger.debug(f"User Credentials: {user_credentials.username}, {user_credentials.password}")

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    # if not user:
    #     logger.debug(f"User not found: {user_credentials.username}")
    # else:
    #     #logger.debug(f"Hashed Password in DB: {user.hashed_password}")
    #     #logger.debug(f"Password verification result: {utils.verify(user_credentials.password, user.hashed_password)}")


    if not user or not utils.verify(user_credentials.password, user.hashed_password):

        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    access_token=  oauth2.create_access_token(data={"user_id": user.id})

    response = RedirectResponse(url="/account/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
    #print(response)
    return response



@router.get('/me', response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(oauth2.get_current_user)):
    return current_user