# ============================================================
# TRIPPILOT - AI PLANNER
# ============================================================

from tools.ai.itinerary import generate_itinerary


# ============================================================
# CREATE AI ITINERARY
# ============================================================

def create_ai_itinerary(
    source,
    destination,
    travel_date,
    days,
    budget,
    interests,
    places,
    hotel,
    transport
):

    return generate_itinerary(
        source=source,
        destination=destination,
        travel_date=travel_date,
        days=days,
        budget=budget,
        interests=interests,
        places=places,
        hotel=hotel,
        transport=transport
    )