from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

 

class UserBase(BaseModel):
    email: EmailStr
    firstname: str   #agregue este y no se si fallara algo pero aca se puede ver............................

class UserCreate(UserBase):
    password: str
    created_at: datetime 


class User(UserBase):
    id: int
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


class UserOut(BaseModel):
    id : int
    email: EmailStr
    is_active: bool
    created_at: datetime


"""
Products schemas
"""

class ProductBase(BaseModel):
    title: str
    category: str
    price: float
    description: str


class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    owner_id: int
    created_at: datetime
    image_url: Optional[str] = None


    """
    Messages schemas

    """

class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    created_at: datetime
    read: bool

