from typing import TypedDict, Literal, NotRequired
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
# ==========================================
# TYPE DEFINITIONS
# ==========================================

AgentName = Literal[
    "hotel",
    "hotel_booking",
    "transport",
    "sightseeing"
]

AgentStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
    "skipped"
]

NextAgent = Literal[
    "hotel",
    "hotel_booking",
    "transport",
    "sightseeing",
    "FINISH"
]


# ==========================================
# AGENT ERROR INFORMATION
# ==========================================

class AgentError(TypedDict):

    error_code: str

    message: str

    retryable: bool


# ==========================================
# INDIVIDUAL AGENT STATE
# ==========================================

class AgentExecutionState(BaseModel):
    status: AgentStatus = "pending"
    attempts: int = 0
    result: str | None = None
    error: AgentError | None = None


# ==========================================
# ORCHESTRATOR DECISION
# ==========================================

class OrchestratorDecision(BaseModel):


    selected_agents: list[AgentName] = Field(
        description=(
            "List of worker agents that should execute "
            "in parallel. Return an empty list if no "
            "further execution is required."
        )
    )
class TravelState(TypedDict):

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    available_agents: list[AgentName]
    agents: dict[AgentName, AgentExecutionState]
    agent_results: Annotated[
        dict[str, str],
        operator.or_
    ]
    retry_count: int
    selected_agents: NotRequired[list[AgentName]]
    final_response: NotRequired[str]
    is_valid: NotRequired[bool]
    verification_feedback: NotRequired[str]
    
    existing_memory: NotRequired[list[str]]
    should_store: NotRequired[Literal["YES", "NO"]]
    extracted_text: NotRequired[str]

class VerificationDecision(BaseModel):

    is_valid: bool = Field(
        description="Whether the generated response satisfies the user's query."
    )

    verification_feedback: str = Field(
        description="Specific explanation of missing or incorrect information. Empty if valid."
    )

class WorkerTask(TypedDict):
    agent_name: AgentName
    query: str
    conversation_context: str

from dataclasses import dataclass

@dataclass
class TravelContext:
    user_id: int

def create_agent_state():
    return {
        "hotel": AgentExecutionState(),
        "hotel_booking":AgentExecutionState(),
        "transport": AgentExecutionState(),
        "sightseeing": AgentExecutionState()
    }