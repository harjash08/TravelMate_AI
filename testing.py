# from core.settings import settings
# import asyncio
# from langchain_mcp_adapters.client import MultiServerMCPClient
# client = MultiServerMCPClient({
#     "1stay": {
#         "transport": "http",
#         "url": "https://mcp.stayker.com/mcp",
#         "headers": {
#             "Authorization": f"Bearer {settings.STAY_API_KEY}"
#         }
#     }
# })


# async def main():
#     tools = await client.get_tools()

#     for tool in tools:
#         print("Tool Name:", tool.name)
#         print("Description:", tool.description)
#         print("-" * 50)


# if __name__ == "__main__":
#     asyncio.run(main())

# Tool Name: search_hotels
# Description: Search hotels by location and dates for exactly one room. Returns available properties with nightly rates across major brands, boutique, and independent hotels.

# The first 1Stay release supports one room per search and reservation. Guest pays the hotel directly. Hotel's own confirmation number. Loyalty points apply.
# --------------------------------------------------
# Tool Name: get_hotel_details
# Description: Get rates and room details for exactly one room at a specific hotel. Returns room types, live rates, amenities, cancellation policies, and rate_codes required by book_hotel.

# Guest pays the hotel directly. Displayed totals include taxes and any applicable, itemized 1Stay Booking Fee. Loyalty points eligible.

# Room type notes: "Run of house" means the hotel assigns the room at check-in. "Suite" at select-service brands usually means a larger room with a sofa, not a separate bedroom.
# --------------------------------------------------
# Tool Name: book_hotel
# Description: Book exactly one hotel room. The first 1Stay release does not support multi-room searches or reservations. Returns a secure checkout URL. This tool accepts no guest identity or payment fields. Name, email, phone, and payment details are collected on the secure checkout page.

# Guest pays the hotel directly. Their credit card statement shows the hotel name, not 1Stay. Hotel's own confirmation number. Loyalty points apply automatically. The displayed total includes taxes and any applicable, itemized 1Stay Booking Fee.

# Requires a rate_code from get_hotel_details, valid approximately 15 minutes. Expired codes are rejected.
# --------------------------------------------------
# Tool Name: lookup_booking
# Description: Look up a reservation by verifying the guest's identity. Returns the confirmation number and booking summary in conversation.

# Requires the guest's full name plus either the hotel confirmation number, or the booking email together with the last 4 digits of the card used to book. An email address alone is not enough. An optional check-in date can narrow repeat stays.
# --------------------------------------------------
# Tool Name: resend_confirmation
# Description: Resend a hotel reservation confirmation email. Use either the confirmation number from a successful lookup_booking call, or the guest's full name and email address when they do not know their confirmation number, card last four, or check-in date. The email contains the hotel confirmation number the guest can then use with lookup_booking or cancel_booking. Recovery requests never reveal whether a reservation matched. The confirmation is sent only to the email address already on the booking record; there is no recipient override. Email changes are handled at https://stayker.com/service.
# --------------------------------------------------
# Tool Name: get_booking
# Description: Look up a reservation exclusively by the hotel confirmation number shown in the guest's confirmation email. Internal Stayker booking IDs are never accepted or disclosed by MCP. Returns full booking details including hotel, dates, guest info, rate, and status.

# Anonymous access requires a verification_token issued by lookup_booking and scoped to a single booking. Without a valid token, no booking data is returned. Developers authenticated with their own API key do not need a token; their access is scoped to their own bookings.
# --------------------------------------------------
# Tool Name: cancel_booking
# Description: Prepare a hotel cancellation for completion on a secure 1Stay page. Verifies the guest's first name, last name, and hotel confirmation number, then returns the hotel policy classification and any cancellation deadline recorded with the reservation, plus a short-lived cancellation_url. 1Stay does not estimate a refund, credit, penalty, or hotel charge. Calling this tool never cancels the reservation. The guest must review the terms and select Cancel reservation on the secure page. A later verified booking-status lookup reporting status cancelled is the authoritative confirmation that the reservation was cancelled.
# --------------------------------------------------
# Tool Name: search_tools
# Description: List available 1Stay hotel booking tools. An optional keyword filters by search, book, cancel, or details; absence of a keyword returns all tools.


from core.settings import settings
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
client = MultiServerMCPClient({

        "fareeagle": {
            "transport": "http",
            "url": "https://www.fareeagle.com/mcp",
        }}
)


async def main():
    tools = await client.get_tools()

    for tool in tools:
        print("Tool Name:", tool.name)
        print("Description:", tool.description)
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())















# **Travel Plan – Goa (15 Dec 2026 – 20 Dec 2026)**  

# ---

# ### 1. Hotel Availability  
# The system could not locate a hotel named **“Celi”** in Goa for the requested dates. Below are the six hotels that were found for a one‑room, single‑guest stay during the same period:

# | # | Hotel (Full name) | Location (city/area) | Approx. total cost for 5 nights (INR) | Avg. nightly rate (INR) |
# |---|-------------------|----------------------|----------------------------------------|--------------------------|
# | 1 | Sea Breeze Sarovar Portico Varca Go | Varca (near Calwaddo) | 32,542 | 6,509 |
# | 2 | Ri Jasminn Goa (Radisson) | Goa (state code GA) | 55,163 | 11,033 |
# | 3 | Fortune Resort Benaulim | Benaulim | 60,773 | 12,155 |
# | 4 | Holiday Inn Resort Goa by IHG | Salcete | 135,889 | 27,178 |
# | 5 | Citadines Arpora Nagoa | Arpora Nagoa | 41,317 | 8,264 |
# | 6 | Taj Exotica Resort & Spa Goa | Calwaddo | 626,754 | 125,351 |

# *All prices are shown exactly as returned by the search agent (INR). No conversion to other currencies was provided.*

# **What to do next**  
# - If you have an alternative hotel name, a more specific area (e.g., “Celi Beach”, “Celia”), or any other preference, let me know and I’ll run a new search.  
# - If one of the hotels above meets your needs, tell me the number of the hotel you’d like to book. I will then retrieve detailed room options and a booking link for you.

# ---

# ### 2. Transportation  
# *No transportation information was returned.*  
# If you need assistance finding flights, trains, or local transfers, please specify the mode of travel, departure city, and any preferences (e.g., budget, class).

# ---

# ### 3. Sightseeing & Activities  
# *No sightseeing information was returned.*  
# If you would like recommendations for attractions, tours, or experiences in Goa (beaches, heritage sites, nightlife, etc.), just let me know your interests and I’ll provide a curated list.

# ---

# ### 4. Next Steps  
# 1. **Confirm or adjust the hotel choice** – provide a new hotel name/area or select one of the six listed.  
# 2. **Specify transportation needs** – origin city, preferred dates, and any class or budget constraints.  
# 3. **Indicate sightseeing preferences** – types of activities or specific places you’d like to visit.

# I’m ready to continue once you let me know how you’d like to proceed.