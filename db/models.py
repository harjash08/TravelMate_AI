from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean
)
from db.database import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

class UserModel(Base):
    __tablename__="user"
    user_id=Column(Integer,primary_key=True,index=True)
    username=Column(String(20),nullable=False)
    password=Column(String(255),nullable=False)
    email=Column(String(50),nullable=False)


class Conversation(Base):
    __tablename__ = "conversation"
    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("user.user_id"),nullable=False)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_message"
    chat_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer,ForeignKey("conversation.conversation_id"), nullable=False)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)