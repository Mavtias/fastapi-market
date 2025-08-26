import os
from fastapi import status, HTTPException, Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from typing import Optional
import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))
router = APIRouter(
    prefix = "/account",
    tags = ['Account']
)


@router.get("/archived", response_class=HTMLResponse)
async def account_archived_ads(request: Request, current_user: models.User = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("account-archived-ads.html", {"request": request, "user": current_user})


@router.get("/close", response_class=HTMLResponse)
async def account_close(request: Request):
    return templates.TemplateResponse("account-close.html", {"request": request})

@router.get("/favourite", response_class=HTMLResponse)
async def account_favourite_ads(request: Request, current_user: models.User = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("account-favourite-ads.html", {"request": request, "user": current_user})


@router.get("/myads", response_class=HTMLResponse)
async def account_myads(request: Request, current_user: models.User = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("account-myads.html", {"request": request, "user": current_user})


@router.get("/profile/setting", response_class=HTMLResponse)
async def account_profile_setting(request: Request, current_user: models.User = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("account-profile-setting.html", {"request": request, "user": current_user})

@router.post("/profile/setting", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    firstname: str = Form(None),
    lastname: str = Form(None),
    address: str = Form(None),
    country: str = Form(None),
    city: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)):
    # Si el campo es vacío, mantener el valor actual de la base de datos
    if firstname:
        current_user.firstname = firstname
    if lastname:
        current_user.lastname = lastname
    if address:
        current_user.address = address
    if country:
        current_user.country = country
    if city:
        current_user.city = city
    
    # Guardar los cambios en la base de datos
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # Redirigir a la misma página de configuración de perfil
    return RedirectResponse("/account/dashboard", status_code=status.HTTP_302_FOUND)




@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, 
                    current_user: models.User = Depends(oauth2.get_current_user), 
                    db: Session = Depends(get_db)):
    user_ads = db.query(models.Product).filter(models.Product.owner_id == current_user.id).order_by(desc(models.Product.created_at)).all()    #probando el obtener solo los ads de un usuario

    return templates.TemplateResponse("dashboard.html", {"request": request, "ads": user_ads, "user": current_user})           #esta funcionaba antes return templates.TemplateResponse("dashboard.html", {"request": request}) 


@router.get("/messages", response_class=HTMLResponse)
async def offermessages(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    conversations = db.query(models.Conversation).filter(
        (models.Conversation.user1_id == current_user.id) |
        (models.Conversation.user2_id == current_user.id)
    ).all()
    
    # Define la conversación por defecto
    conversation = conversations[0] if conversations else None
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation.id if conversation else None
    ).order_by(models.Message.created_at).all() if conversation else []

    return templates.TemplateResponse("offermessages.html", {
        "request": request,
        "user": current_user,
        "conversations": conversations,
        "messages": messages,
        "conversation": conversation  # Agregamos la conversación
    })

@router.get("/messages/{conversation_id}", response_class=HTMLResponse)
async def view_conversation(request: Request, 
                            conversation_id: int, 
                            db: Session = Depends(get_db),
                            current_user: models.User = Depends(oauth2.get_current_user)):
    
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        (models.Conversation.user1_id == current_user.id) | 
        (models.Conversation.user2_id == current_user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    # Obtener los mensajes de la conversación
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at).all()
    
    return templates.TemplateResponse("conversation.html", {"request": request, "user": current_user, "conversation": conversation, "messages": messages})

@router.post("/messages/{conversation_id}")
async def send_message(
    request: Request,
    conversation_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)):
    
    new_message = models.Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content
    )
    db.add(new_message)
    db.commit()
    return RedirectResponse(f"/account/messages", status_code=status.HTTP_302_FOUND)



@router.post("/logout")
async def logout(request: Request):
    response = RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token", httponly=True, secure=True, path="/")
    return response