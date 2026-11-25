from langchain_core.prompts import ChatPromptTemplate
from graph.state import TravelState
from langchain_core.messages import AIMessage
from core.mesh_config import model
GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are TravelMate, an intelligent travel planning assistant.

        YOUR RESPONSIBILITIES:

        1. Combine the results provided by specialized agents.
        2. Prepare a clear and well-organized travel plan.
        3. Avoid repeating information.
        4. Organize information into meaningful sections.
        5. Respect the user's original requirements.
        6. Clearly mention when requested information is unavailable.

        IMPORTANT RULES:

        - Use only the information provided by the agents.
        - Never invent hotel prices, transportation fares,
          ratings or availability.
        - Do not claim that any booking has been completed
          unless confirmed by the relevant agent.
        - If an agent failed, clearly communicate that
          its information could not be retrieved.
        - Do not hide incomplete results.

        RESPONSE STYLE:

        - Use simple and professional language.
        - Use headings and bullet points.
        - Make the travel plan easy to understand.
        """
    ),
    (
        "human",
        """
        ORIGINAL USER QUERY:

        {query}

        HOTEL RESULTS:

        {hotel_results}

         HOTEL Booking RESULTS:
        
        {hotel_booking_results}

        TRANSPORT RESULTS:

        {transport_results}

        SIGHTSEEING RESULTS:

        {sightseeing_results}

        Prepare the final travel response.
        """
    )
])




from core.logger import get_logger, track_execution
logger = get_logger(__name__)


@track_execution
async def generator_node(state: TravelState):
    logger.info("Generator execution started")

    # Collect results from specialized agents
    agent_results = state.get("agent_results", {})

    # Prepare generator input
    prompt = GENERATOR_PROMPT.invoke({
        "query": state["query"],

        "hotel_results": agent_results.get(
            "hotel", "Hotel information unavailable."
        ),

        "hotel_booking_results": agent_results.get(
                    "hotel_booking", "Hotel Booking  information unavailable."
                ),

        "transport_results": agent_results.get(
            "transport", "Transportation information unavailable."
        ),

        "sightseeing_results": agent_results.get(
            "sightseeing", "Sightseeing information unavailable."
        )
    })

    # Generate final travel response
    response = await model.ainvoke(prompt)
    print("Generator Response: ",response)

    return {
        "final_response": response.content,
        "messages": [
        AIMessage(content=response.content)
    ]
    }