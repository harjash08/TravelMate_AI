from fastapi import APIRouter,Depends,UploadFile, File,Request,Form,BackgroundTasks
from schemas.user import *
from db.database import get_db
from sqlalchemy.orm import Session
from db.models import *
from fastapi import APIRouter,Depends,HTTPException,Request,BackgroundTasks
from pwdlib import PasswordHash
from schemas.travel_chat_schema import *
from datetime import datetime, timedelta, timezone
from core.settings import settings
from graph.state import TravelContext
from core.helper import is_authenticated
from core.security import create_access_token
from graph.state import create_agent_state
from langchain_core.messages import HumanMessage
import traceback
chatrouter=APIRouter()

@chatrouter.post("/conversation/",response_model=conversation_response)
def conversation(current_user:UserModel=Depends(is_authenticated),db:Session=Depends(get_db)):
    conversation = Conversation(
    user_id=current_user.user_id,
    title=None
)

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation     

@chatrouter.get("/get_conversation/",response_model=conversation_response)
def conversation(current_user:UserModel=Depends(is_authenticated),db:Session=Depends(get_db)):
    conversation = db.query(Conversation).filter(
         Conversation.user_id == current_user.user_id).order_by(
              Conversation.conversation_id.desc()).all()

    return conversation  

@chatrouter.post("/chat/{conversation_id}/",response_model=chat_response)
async def chat(body:create_chat,request:Request,conversation_id:int,current_user_id:UserModel=Depends(is_authenticated),db:Session=Depends(get_db)):
    conversation=db.query(Conversation).filter(
        Conversation.conversation_id==conversation_id,
        Conversation.user_id==current_user_id
    ).first()
    if not conversation:
        if not conversation:
            print("Conversation not found")
        raise HTTPException(
            status_code=404,
            detail="Conversation not found" )
    user_message=body.message
    chat=ChatMessage(
        conversation_id = conversation_id,
        role = "user",
        message = user_message
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.close()

    graph = request.app.state.travel_graph

    

    initial_state = {
    "query": user_message,
    "messages": [HumanMessage(content=user_message)],
    "available_agents": ["hotel","hotel_booking", "transport", "sightseeing"],
    # "selected_agents": [],
    # "agent_results": {},
    # "agents": create_agent_state(),
    # "final_response": ""
}
    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }
    try:
        result = await graph.ainvoke(
            initial_state,
            config,
            context=TravelContext(
                user_id=current_user_id
            ))
        print("Result: ",result)
        print("\n===== CHECKPOINT MESSAGE HISTORY =====")

        for message in result.get("messages", []):
            print(message.type, ":", message.content)

        print("======================================")

    except Exception as e:
        print("GRAPH EXECUTION FAILED")
        print("ERROR:", str(e))
        traceback.print_exc()
        raise

    interrupts = result.get("__interrupt__", [])

    if interrupts:

        return {
            "status": "approval_required",
            "conversation_id": conversation_id,
            "interrupts": [
                interrupt.value
                for interrupt in interrupts
            ]
        }

    response= result["final_response"]
    print("Response: ",response)
    
    
    try:
        chat = ChatMessage(
            conversation_id=conversation_id,
            role="ai",
            message=response
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

    except Exception:
        db.rollback()
        raise

    return chat


from typing import Literal
from pydantic import BaseModel
from langgraph.types import Command


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]


@chatrouter.post("/chat/{conversation_id}/approval")
async def handle_approval(
    conversation_id: int,
    body: ApprovalRequest,
    request: Request,
    current_user_id: UserModel = Depends(is_authenticated),
    db: Session = Depends(get_db)
):

    # 1. Verify conversation ownership
    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id,
        Conversation.user_id == current_user_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    graph = request.app.state.travel_graph

    # 2. Use the SAME thread ID
    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    # 3. Resume interrupted execution
    result = await graph.ainvoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": body.decision
                    }
                ]
            }
        ),
        config=config,
        context=TravelContext(
            user_id=current_user_id
        )
    )

    # 4. Check whether another approval is required
    interrupts = result.get("__interrupt__", [])

    if interrupts:

        return {
            "status": "approval_required",
            "conversation_id": conversation_id,
            "interrupts": [
                interrupt.value
                for interrupt in interrupts
            ]
        }

    # 5. Save final response
    response = result["final_response"]

    chat_message = ChatMessage(
        conversation_id=conversation_id,
        role="ai",
        message=response
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return {
        "status": "completed",
        "response": response
    }