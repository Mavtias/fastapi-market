from sqlalchemy.orm import Session
from models import Conversation, Message, User

def get_or_create_conversation(db: Session, user1_id: int, user2_id: int):
    conversation = db.query(Conversation).filter(
        ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
        ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
    ).first()

    if not conversation:
        conversation = Conversation(user1_id=user1_id, user2_id= user2_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation

def create_message(db: Session, conversation_id: int, sender_id: int, content: str):
    message = Message(conversation_id=conversation_id, sender_id= sender_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, conversation_id: int, skip: int=0, limit: int = 10):
    return db.query(Message).filter(Message.conversation_id == conversation_id).offset(skip).limit(limit).all()