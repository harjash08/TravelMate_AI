from graph.state import WorkerTask
from core.logger import get_logger, track_execution
logger = get_logger(__name__)


@track_execution
def create_worker_node(travel_agents):
    logger.info("Worker execution started")
    async def worker_node(task: WorkerTask):
        logger.info("Worker execution started")

        agent_name = task["agent_name"]
        query = task["query"]
        context = task["conversation_context"]

        agent = travel_agents.get(agent_name)

        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        result = await agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                    PREVIOUS CONVERSATION:
                    {context}
                    ORIGINAL USER QUERY:
                    {query}

                    
                    """
                }
            ]
        })
        agent_response = result["messages"][-1].content

        print("Agent:", agent_name)
        print("Response length:", len(agent_response))
        print("Worker Response:", agent_response)
        
        return {
            "agent_results": {
                agent_name: result["messages"][-1].content
            }
        }

    return worker_node