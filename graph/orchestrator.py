from graph.state import TravelState, OrchestratorDecision
from graph.prompt import ORCHESTRATOR_PROMPT

from core.mesh_config import model
from core.logger import get_logger, track_execution


logger = get_logger(__name__)

orchestrator_llm = model.with_structured_output(
    OrchestratorDecision
)


@track_execution
async def orchestrator_node(state: TravelState):
    

    logger.info("Orchestrator execution started")
    logger.info("Available agents: %s", state["available_agents"])
    logger.info("User query: %s", state["query"])
    logger.info("Previous results: %s", state["agent_results"])

    prompt = ORCHESTRATOR_PROMPT.invoke({

        "query": state["query"],

        "available_agents": state["available_agents"],

        "agent_results": state.get("agent_results", []),

        "verification_feedback": state.get(
            "verification_feedback", ""
        )
    })

    decision = await orchestrator_llm.ainvoke(prompt)

    selected_agents = decision.selected_agents

    logger.info(
        f"Selected agents: {selected_agents}"
    )

    # If new worker execution is required,
    # remove previous results to avoid mixing old and new results.

    if selected_agents:

        return {
            "selected_agents": selected_agents,
            "agent_results": {}
        }

    return {
        "selected_agents": []
    }