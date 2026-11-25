from pydantic import BaseModel
from typing import Any

class create_conversation(BaseModel):
    user_id:int
    title:str | None=None

class conversation_response(BaseModel):
    conversation_id :int
    user_id :int
    title :str

class create_chat(BaseModel):
    message :str

class ApprovalResponse(BaseModel):
    status: str
    conversation_id: int
    interrupts: list[dict[str, Any]]


class chat_response(BaseModel):
    status: str | None = None
    conversation_id: int | None = None
    chat_id: int | None = None
    role: str | None = None
    message: str | None = None
    interrupts: list[dict[str, Any]] | None = None