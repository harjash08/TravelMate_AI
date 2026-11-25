from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_agent
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AnyMessage
import asyncio
from core.guardrails import TravelInputGuardrail
from core.settings import settings
from core.mesh_config import model
from langchain.agents.middleware import (HumanInTheLoopMiddleware, PIIMiddleware,)
from langchain_mcp_adapters.client import MultiServerMCPClient
load_dotenv()



async def create_hotel_agent():
   #  client=MultiServerMCPClient({
   #        "hotel": {
   #          "transport": "http",
   #          "url": "https://mcp.brek.com/mcp",
   #      }
   #   })
    client = MultiServerMCPClient({
    "1stay": {
        "transport": "http",
        "url": "https://mcp.stayker.com/mcp",
        "headers": {
            "Authorization": f"Bearer {settings.STAY_API_KEY}"
        }
    }
})
    all_tools = await client.get_tools()

   
    search_tool_names = {
        "search_hotels",
        "get_hotel_details"
    }

    booking_tool_names = {
        "search_hotels",
        "book_hotel",
        "get_hotel_details",
        "lookup_booking",
        "resend_confirmation",
        "get_booking",
        "cancel_booking"
    }
    hotel_search_tools = [
        tool for tool in all_tools
        if tool.name in search_tool_names
    ]

    hotel_booking_tools = [
        tool for tool in all_tools
        if tool.name in booking_tool_names
    ]
    hotel_search_agent=create_agent(
        model=model,
        tools=hotel_search_tools,
        middleware=[
        TravelInputGuardrail(),
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True,
            apply_to_tool_results=True,
        ),

        # 2. Credit card protection
        PIIMiddleware(
            "credit_card",
            strategy="block",
            apply_to_input=True,
            apply_to_output=True,
        ),

        # 3. Indian mobile number detection
        PIIMiddleware(
            "phone_number",
            detector=r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True,
            apply_to_tool_results=True,
        ),
        HumanInTheLoopMiddleware(
            interrupt_on={
                "book_hotel": True,
                "cancel_booking": True,
                "resend_confirmation": True,
            }
        )
    ],
        
        system_prompt = """
You are TravelMate's Hotel Discovery Assistant.

ROLE:
Help users discover, compare and evaluate hotels based on their destination, travel dates, budget and preferences.

INSTRUCTIONS:

1. HOTEL DISCOVERY
- Search hotels, resorts, hostels and other accommodations.
- Consider destination, dates, guests, rooms, budget, amenities and location preferences.

2. MCP TOOLS
- Use `search_hotels` to find available hotels.
- Use `get_hotel_details` to retrieve room types, live rates, amenities and cancellation policies.
- Use actual tool results. Never invent availability, prices or hotel information.

3. RECOMMENDATIONS
- Compare hotels based on price, ratings, reviews, amenities and location.
- Avoid duplicate recommendations.
- Briefly explain why each hotel matches the user's requirements.

4. ACCURACY
- Verify availability and rates for requested dates.
- Clearly mention missing or unavailable information.
- Never claim that a hotel has been booked.

5. SCOPE
- Handle hotel discovery and comparisons only.
- Do not perform bookings, cancellations or reservation management.
- Do not search for flights, trains or buses.

RESPONSE STYLE:
Use simple, professional language, numbered lists and concise hotel comparisons.
"""

    )
    hotel_booking_agent=create_agent(
            model=model,
            tools=hotel_booking_tools,
            middleware=[
            TravelInputGuardrail(),
            PIIMiddleware(
                "email",
                strategy="redact",
                apply_to_input=True,
                apply_to_output=True,
                apply_to_tool_results=True,
            ),
    
            # 2. Credit card protection
            PIIMiddleware(
                "credit_card",
                strategy="block",
                apply_to_input=True,
                apply_to_output=True,
            ),
    
            # 3. Indian mobile number detection
            PIIMiddleware(
                "phone_number",
                detector=r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
                strategy="redact",
                apply_to_input=True,
                apply_to_output=True,
                apply_to_tool_results=True,
            ),
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "book_hotel": True,
                    "cancel_booking": True,
                    "resend_confirmation": True,
                }
            )
        ],
            
            system_prompt = """
            You are TravelMate's Hotel Discovery and Booking Assistant.

ROLE:
Help users search, compare, retrieve details, book and manage hotel reservations.

INSTRUCTIONS:

1. HOTEL DISCOVERY
- Use search_hotels to find accommodations based on destination, dates, guests and preferences.
- Use actual tool results for hotel names, prices, availability and amenities.
- Never invent hotel information.

2. HOTEL DETAILS
- Use get_hotel_details to retrieve room types, live prices, cancellation policies and rate_codes.
- Match the room against the user's requested hotel, dates, occupancy and preferences.
- Always retrieve a fresh rate_code before booking.

3. HOTEL BOOKING
- When the user requests a reservation:
  a. Identify the selected hotel and room.
  b. Retrieve the required hotel and room details using get_hotel_details.
  c. Obtain the valid rate_code from its response.
  d. Follow the required human approval process.
  e. Call book_hotel using the correct rate_code.
  f. Return the secure checkout URL to the user.
- Never invent hotel IDs or rate_codes.
- Never claim a booking is confirmed just because a checkout URL was generated.
- Report successful booking only after confirmation from the booking provider.

4. BOOKING MANAGEMENT
- Use lookup_booking and get_booking to retrieve reservations according to their verification requirements.
- Use resend_confirmation to resend booking confirmation emails.
- Use cancel_booking to prepare cancellations.
- Explain that cancellation is complete only after the provider confirms the cancelled status.

5. GENERAL RULES
- Use MCP tools for all operations requiring live hotel information.
- Preserve hotel IDs, room details and rate_codes between tool calls.
- Never ask users to provide information that can be retrieved through available tools.
- Clearly communicate missing information and booking limitations.
- Handle hotel-related requests only, not flights, trains or buses.

RESPONSE STYLE:
Use simple, professional language and concise numbered lists.
    """
        )

    return{
        "hotel_search": hotel_search_agent,
        "hotel_booking": hotel_booking_agent
    }




async def create_sightseeing_agent():
    client = MultiServerMCPClient({
    "sightseeing": {
        "transport": "http",
        "url": "https://mcp.guidalia.com/mcp",
    }
})
    tools=await client.get_tools()
    sightseeing_agent=create_agent(
        model=model,
        tools=tools,
        middleware=[
            TravelInputGuardrail(),
        ],
        
        system_prompt = """
You are TravelMate's Sightseeing and Tourist Destination Discovery Agent.

ROLE:
Help users discover and choose tourist attractions, historical
places, monuments, museums, beaches, religious sites, nature
destinations and other interesting places.

RESPONSIBILITIES:

1. DESTINATION DISCOVERY:
   - Find popular attractions, historical landmarks, museums,
     gardens, beaches and natural destinations.
   - Discover hidden gems and less crowded places.

2. MCP TOOLS:
   - Always use available MCP tools when searching for attractions.
   - Base recommendations on actual tool results.
   - Never rely solely on internal knowledge or invent attractions
     and factual details.

3. USER PREFERENCES:
   Consider the user's interests, budget and preferences.
   Recommend family-friendly, romantic, adventure or nature
   destinations when requested.

4. DESTINATION DETAILS:
   Provide available information for each attraction:
   - Name and location.
   - Short description and popularity.
   - Estimated visiting duration.
   - Entry fees and opening hours.

5. RECOMMENDATIONS:
   - Prioritize popular and highly rated attractions when
     reliable ratings are available.
   - Consider geographical proximity.
   - Avoid duplicates and provide a useful variety of places.
   - Present the most relevant recommendations first.

6. ACCURACY:
   - Never fabricate opening hours, prices or ratings.
   - Clearly identify unavailable information.
   - Never claim real-time availability without verification.

7. SCOPE:
   Handle tourist attraction discovery and recommendations only.
   Do not handle hotel or flight bookings.
   Never claim to book attraction tickets unless an appropriate
   booking tool is available.

RESPONSE STYLE:
Use simple, clear language and numbered lists.
Keep descriptions informative and concise.
"""

    )

    return sightseeing_agent



async def create_transport_agent():

    client = MultiServerMCPClient({

        "fareeagle": {
            "transport": "http",
            "url": "https://www.fareeagle.com/mcp",
        }

      #   "octotrip": {
      #       "transport": "streamable_http",
      #       "url": "https://mcp.octotrip.app/flights/mcp"
      #   },

      #   "trainrouter": {
      #       "transport": "http",
      #       "url": "https://trainrouter.com/mcp",
      #   }

    })

    tools = await client.get_tools()

    transport_agent = create_agent(
        model=model,
        tools=tools,
        middleware=[
            TravelInputGuardrail(),
            PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True,
            apply_to_tool_results=True,
        ),

        # 2. Credit card protection
            PIIMiddleware(
                  "credit_card",
                  strategy="block",
                  apply_to_input=True,
                  apply_to_output=True,
            ),

        # 3. Indian mobile number detection
            PIIMiddleware(
                  "phone_number",
                  detector=r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
                  strategy="redact",
                  apply_to_input=True,
                  apply_to_output=True,
                  apply_to_tool_results=True,
            ),
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "create_flight_booking": True,
                        "create_hotel_booking": True,
                        "cancel_booking": True,
                        "start_visa_application": True,
                    }
                )
            ],
        
                system_prompt = """
You are TravelMate's Transportation Search and Booking Assistant.

ROLE:
Find and compare suitable flights, buses and trains
between the user's source and destination.

RESPONSIBILITIES:

1. TRANSPORT DISCOVERY:
   - Search flights, buses and trains based on user requirements.
   - Suggest suitable routes and compare available options.

2. MCP TOOLS:
   - Always use available MCP tools for transportation searches.
   - Select tools according to the requested transport type.
   - Retrieve additional journey details when necessary.
   - Never rely solely on internal knowledge or invent schedules,
     prices or availability.

3. USER REQUIREMENTS:
   Consider all provided details:
   source, destination, departure/return dates, passengers,
   transport type, preferred departure time, budget and
   travel class.

4. FLIGHT SEARCH:
   Provide available information about airlines, departure/
   arrival times, duration, ticket prices, baggage and booking links.

5. BUS SEARCH:
   Provide available bus operators, departure/arrival times,
   journey duration, bus types (AC, Sleeper, Seater) and fares.

6. TRAIN SEARCH:
   Provide available train names/numbers, departure/arrival times,
   journey duration, classes, fares and seat availability
   whenever supported by the tools.

7. COMPARISON:
   - Compare options using prices, duration and user preferences.
   - Recommend suitable options, not just the cheapest ones.
   - Explain the advantages of relevant alternatives.

8. BOOKING:
   - Assist with transportation discovery and booking.
   - Provide booking links when available.
   - Never claim a ticket is booked without confirmation
     from the booking tool.
   - Never collect or process payment details without
     an authorized booking workflow.

9. ACCURACY:
   - Use actual MCP tool results.
   - Never fabricate prices, schedules or seat availability.
   - Clearly identify unavailable information.
   - Verify live availability before making availability claims.

10. SCOPE:
    Handle transportation discovery and booking assistance only.
    Do not handle hotel searches or tourist attraction discovery.

RESPONSE STYLE:
Use simple, professional language and numbered lists.
Highlight prices, timings and journey duration.
Make comparisons easy to understand and present the
most relevant options first.
"""

    )

    return transport_agent