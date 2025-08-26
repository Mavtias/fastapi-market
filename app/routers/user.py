from fastapi import status, HTTPException, Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, utils, database
from ..database import get_db
from typing import Optional
import os

#templates = Jinja2Templates(directory = "../templates")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

router = APIRouter(
    prefix = "/users",
    tags = ['Users']
)

@router.post("/signup", response_model = schemas.UserOut)
def register(
            firstname: str = Form(...),
            lastname: str = Form(...),
            country: str = Form(...),
            email: str = Form(...), 
            password: str = Form(...), 
            password_confirm : str = Form(...), 
            db:Session = Depends(database.get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if password != password_confirm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passwords do not match")

    

    hashed_password = utils.hash(password)
    password = hashed_password
    db_user = models.User(firstname = firstname, lastname = lastname, country = country, email=email, hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)



 
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})

