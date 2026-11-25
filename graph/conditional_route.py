from langgraph.types import Send
from graph.state import TravelState

from core.logger import get_logger, track_execution
logger = get_logger(__name__)


@track_execution
def dispatch_workers(state: TravelState):
    logger.info("Dispatch Worker execution started")

    selected_agents = state.get("selected_agents", [])

    # No more workers to execute
    if not selected_agents:
        return "generator"

    recent_messages = state.get("messages", [])[-4:]

    conversation_context = "\n".join(
        f"{message.type}: {message.content}"
        for message in recent_messages
    )
    # Dispatch selected workers in parallel
    return [
        Send(
            "agent_executor",
            {
                "agent_name": agent,
                "query": state["query"],
                "conversation_context": conversation_context
            }
        )
        for agent in selected_agents
    ]


@track_execution
def verification_router(state: TravelState):
    logger.info("Verification router execution started")
    logger.info(
    f"ROUTING: is_valid={state.get('is_valid')}, "
    f"retry_count={state.get('retry_count', 0)}"
)
    if state.get("is_valid"):
        return "end"

    if state.get("retry_count", 0) >= 2:
        return "end"

    return "orchestrator"