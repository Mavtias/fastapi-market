from fastapi import status, HTTPException, Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from typing import Optional
import os

#templates = Jinja2Templates(directory = "../templates")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

router = APIRouter(
    prefix = "",
    tags = ['Misc']
)


@router.get("/404", response_class=HTMLResponse)
async def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, user: models.User = Depends(oauth2.get_optional_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, user: models.User = Depends(oauth2.get_optional_user)):
    return templates.TemplateResponse("contact.html", {"request": request, "user":user})


@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request,  user: models.User = Depends(oauth2.get_optional_user)):
    return templates.TemplateResponse("faq.html", {"request": request, "user":user})

@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request, user: models.User = Depends(oauth2.get_optional_user)):
    return templates.TemplateResponse("pricing.html", {"request": request, "user":user})