from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from .database import Base

"""

Creating the database models

"""


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True, nullable = False, index=True)
    firstname = Column(String, nullable = False, unique = False)
    lastname = Column(String, nullable = False, unique = False)
    email = Column(String, nullable = False, unique = True, index=True)
    address = Column(String, nullable = True, unique = False)
    country = Column(String, nullable = True, unique = False)
    city = Column(String, nullable = True, unique = False)
    hashed_password = Column(String, nullable = False)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = True)
    is_fake = Column(Boolean, default=False)

    products = relationship("Product", back_populates="owner")



class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key = True, index= True)
    title = Column(String, index= True, nullable = False)
    category = Column(String, nullable = False)
    price = Column(Float, nullable = False)
    description = Column(Text, nullable = False)
    image_url = Column(String, nullable = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"))
    is_fake = Column(Boolean, default=False)



    owner = relationship("User", back_populates="products")



#### Implementing conversations models

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key = True, index= True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = True)

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")



class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key = True, index= True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = True)
    read = Column(Boolean, default=False)
    
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")