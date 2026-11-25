from langgraph.graph import StateGraph, START, END
from graph.memory import *
from graph.state import TravelState
from graph.orchestrator import orchestrator_node
from graph.conditional_route import dispatch_workers,verification_router
from graph.worker import create_worker_node
from graph.generator import generator_node
from graph.verification import verification_node
from core.logger import get_logger, track_execution
from fastapi import Request
logger = get_logger(__name__)


@track_execution
def create_travel_graph(travel_agents,store,checkpointer):
    logger.info("Graph execution started")

    builder = StateGraph(TravelState)

    # Register nodes
    builder.add_node("load_memory", load_memory)
    builder.add_node("is_memory_required", is_memory_required)
    builder.add_node("text_extraction", text_extraction)
    builder.add_node("save_memory", save_memory)

    builder.add_node(
        "agent_executor",
        create_worker_node(travel_agents)
    )

    builder.add_node("generator", generator_node)
    builder.add_node("verification_node", verification_node)
    builder.add_node("orchestrator", orchestrator_node)
    # Starting point
    builder.add_edge(START, "load_memory")
    builder.add_edge("load_memory", "is_memory_required")
    builder.add_conditional_edges("is_memory_required", memory_decision_node,{"text_extraction":"text_extraction","orchestrator":"orchestrator"})
    builder.add_edge("text_extraction", "save_memory")
    builder.add_edge("save_memory", "orchestrator")

    # Orchestrator -> Workers or Generator
    builder.add_conditional_edges(
        "orchestrator",
        dispatch_workers,
        {
            "generator": "generator"
        }
    )

    # Workers -> Orchestrator
    # builder.add_edge("agent_executor", "orchestrator")
    builder.add_edge("agent_executor", "generator")


    builder.add_edge("generator", "verification_node")
    builder.add_conditional_edges("verification_node",verification_router,{"end":END,"orchestrator":"orchestrator"})
    return builder.compile(store=store,checkpointer=checkpointer)