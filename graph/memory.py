import hashlib
from typing import Literal

from pydantic import BaseModel
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.logger import get_logger, track_execution
from graph.state import TravelState, TravelContext
from core.mesh_config import model

logger = get_logger(__name__)


class MemoryDecision(BaseModel):
    decision: Literal["YES", "NO"]


@track_execution
async def load_memory(state: TravelState,runtime: Runtime[TravelContext]):
    logger.info("load_memory started")
    user_id = runtime.context.user_id

    namespace = (f"user_{user_id}", "memories")

    memories =runtime.store.search(
        namespace,
        limit=20
    )

    existing_memory = [
        item.value["text"]
        for item in memories
        if "text" in item.value
    ]

    return {
        "existing_memory": existing_memory
    }


# ==========================================
# 3. Check Whether Memory Is Required
# ==========================================
@track_execution
async def is_memory_required(
    state: TravelState,
    runtime: Runtime[TravelContext]
):
    logger.info("is_memory_required started")

    user_question = state["query"]
    existing_memory = state.get("existing_memory", [])

    prompt = PromptTemplate.from_template("""
    You are the long-term memory decision system for TravelMate, an AI-powered travel planning and booking assistant.

Your responsibility is to determine whether the user's message contains useful, long-term information that should be saved to personalize future travel experiences.

RULES:

1. Return YES when the user shares new, useful information such as:
   - Travel preferences (preferred airlines, hotels, accommodation types).
   - Preferred travel destinations or travel interests.
   - Budget preferences for flights, hotels, and vacations.
   - Preferred travel styles (luxury, budget, adventure, leisure, business).
   - Preferred transportation methods.
   - General booking preferences.
   - Long-term travel plans or recurring travel goals.
   - Explicit preferences about how TravelMate should assist them.

2. Return NO for:
   - Greetings and casual conversations.
   - General knowledge questions about travel.
   - Temporary travel queries that are relevant only to the current conversation.
   - One-time flight or hotel searches.
   - Information that is already stored in memory.
   - Information that is too vague to be useful in future interactions.

3. Compare the user's message with existing memories before making a decision.

4. Consider semantic similarity, not just exact wording. For example:
   - Existing memory: The user prefers budget hotels.
   - New message: I usually look for affordable accommodation.
   - Decision: NO.

5. Return YES when the user provides an update or correction to an existing preference that should replace the old information.

6. Do not store sensitive personal information, payment credentials, passwords, authentication tokens, or confidential booking information.

7. Only consider information explicitly provided by the user. Never infer personal preferences.

INPUT:

User Message:
{user_question}

Existing Memories:
{existing_memory}

OUTPUT:

Return a valid JSON object using this exact structure:

{{
    "decision": "YES"
}}

OR

{{
    "decision": "NO"
}}

The decision must be either YES or NO.
Do not include explanations.
    """)

    structured_llm = model.with_structured_output(MemoryDecision, method="json_mode")

    chain = prompt | structured_llm

    result = await chain.ainvoke({
        "user_question": user_question,
        "existing_memory": existing_memory
    })

    return {
        "should_store": result.decision
    }


# ==========================================
# 4. Memory Decision Router
# ==========================================

def memory_decision_node(
    state: TravelState
) -> Literal["text_extraction", "retrieval_node"]:

    if state["should_store"] == "YES":
        return "text_extraction"

    return "orchestrator"


# ==========================================
# 5. Extract Useful Memory
# ==========================================
@track_execution
async def text_extraction(state: TravelState):
    logger.info("text_Extraction started")

    user_message = state["query"]

    prompt = PromptTemplate.from_template("""
    You are the long-term memory extraction system for TravelMate, an AI-powered travel planning and booking assistant.

    Your responsibility is to extract useful, meaningful, and reusable information from the user's message that can help TravelMate personalize future travel recommendations and booking experiences.

    RULES:

    1. Write extracted memories in third person, starting with "The user".

    2. Extract useful long-term information, including:
    - Travel preferences and interests.
    - Preferred destinations or types of destinations.
    - Hotel and accommodation preferences.
    - Preferred airlines and flight preferences.
    - Preferred seating preferences.
    - Travel budget preferences.
    - Preferred transportation methods.
    - Travel styles such as luxury, budget, adventure, leisure, or business.
    - Recurring travel requirements.
    - Long-term travel plans and goals.
    - Preferences about how TravelMate should assist the user.

    3. Preserve the original meaning without inventing or assuming information.

    4. Convert the information into short, clear, standalone statements that remain understandable without the original conversation.

    5. Ignore:
    - Greetings and casual conversations.
    - General travel-related questions.
    - Temporary search requests.
    - One-time flight or hotel booking requirements.
    - Information that is not useful for future travel interactions.

    6. Do not extract sensitive personal information, payment credentials, passwords, authentication tokens, or confidential booking information.

    7. If the user updates an existing preference, extract the new preference clearly so that the memory system can update the previous one.

    8. If the message contains multiple useful preferences, extract them as separate memory statements.

    9. If no useful long-term information exists, return NONE.

    10. Return only the extracted memories without explanations or additional text.

    EXAMPLES:

    User Message:
    "I usually prefer luxury hotels with swimming pools."

    Memory:
    The user prefers luxury hotels with swimming pools.

    User Message:
    "I prefer window seats when booking flights."

    Memory:
    The user prefers window seats when booking flights.

    User Message:
    "I generally travel on a limited budget."

    Memory:
    The user prefers budget-friendly travel options.

    User Message:
    "I enjoy adventure trips and exploring mountains."

    Memory:
    The user enjoys adventure travel and mountain destinations.

    User Message:
    "Find me a hotel in Goa for tomorrow."

    Memory:
    NONE

    User Message:
    "I now prefer luxury hotels instead of budget hotels."

    Memory:
    The user now prefers luxury hotels over budget hotels.

    User Message:
    "Hi, how are you?"

    Memory:
    NONE

    USER MESSAGE:

    {user_message}
    """)

    chain = prompt | model | StrOutputParser()

    extracted_text = await chain.ainvoke({
        "user_message": user_message
    })

    return {
        "extracted_text": extracted_text.strip()
    }


# ==========================================
# 6. Save Memory
# ==========================================
@track_execution
async def save_memory(
    state: TravelState,
    runtime: Runtime[TravelContext]
):
    logger.info("save_memory started")

    extracted_text = state.get("extracted_text", "").strip()

    if not extracted_text or extracted_text.upper() == "NONE":
        return {}

    user_id = runtime.context.user_id

    namespace = (f"user_{user_id}", "memories")

    # Deterministic key for exact duplicate prevention
    key = hashlib.sha256(
        extracted_text.lower().encode("utf-8")
    ).hexdigest()

    runtime.store.put(
        namespace,
        key,
        {"text": extracted_text}
    )

    return {}