# ============================================================
# TRIPPILOT - GEMINI AI ITINERARY GENERATOR
# ============================================================

import os

from dotenv import load_dotenv
import google.generativeai as genai


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not GOOGLE_API_KEY:

    raise ValueError(
        "\n❌ GOOGLE_API_KEY not found in .env\n"
        "\nAdd this to your .env file:\n\n"
        "GOOGLE_API_KEY=your_api_key_here\n"
    )


# ============================================================
# CONFIGURE GEMINI
# ============================================================

genai.configure(
    api_key=GOOGLE_API_KEY
)


# ============================================================
# GEMINI MODEL
# ============================================================

model = genai.GenerativeModel(
    "gemini-3.6-flash"
)


# ============================================================
# GENERATE AI ITINERARY
# ============================================================

def generate_itinerary(
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

    prompt = f"""
You are TripPilot, an intelligent AI travel planner.

Your job is to create a realistic and personalized
day-wise travel itinerary using ONLY the information
provided below.

============================================================
TRIP DETAILS
============================================================

Starting City:
{source}

Destination:
{destination}

Travel Date:
{travel_date}

Number of Days:
{days}

Total Budget:
₹{budget}

Interests:
{interests}


============================================================
TRANSPORT INFORMATION
============================================================

{transport}


============================================================
HOTEL INFORMATION
============================================================

{hotel}


============================================================
AVAILABLE PLACES
============================================================

{places}


============================================================
IMPORTANT RULES
============================================================

1. The trip destination is:

{destination}

2. Every recommended place MUST belong to the destination.

3. ONLY use places provided in AVAILABLE PLACES.

4. NEVER invent tourist attractions.

5. NEVER use places from another city.

6. NEVER invent hotels.

7. ONLY use the supplied hotel information.

8. NEVER invent transport prices.

9. NEVER invent flight fares.

10. NEVER invent train fares.

11. NEVER invent bus fares.

12. If transport price is unavailable, clearly say:
"Transport fare unavailable."

13. If hotel price is unavailable, clearly say:
"Hotel price unavailable."

14. Keep the itinerary realistic.

15. Avoid scheduling too many places in one day.

16. Group geographically close places together when possible.

17. Consider travel time.

18. Consider the user's interests.

19. Consider the user's total budget.

20. The first day should consider arrival time.

21. The final day should consider departure time.

22. Do not claim that a place is open at a particular
time unless opening information is supplied.

23. Do not create fake prices.

24. If there are not enough places for all days,
use:

"Free time / explore locally"

instead of inventing places.

25. Optional activities must be clearly marked as optional.

26. Do not repeat the same place unnecessarily.

27. Prefer 1-3 meaningful activities per day.

28. Make the itinerary useful for a real traveler.

29. Keep the answer easy to read.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY the itinerary.

Use this exact structure:

DAY 1
------------------------------------------------------------
Morning:
- Activity

Afternoon:
- Activity

Evening:
- Activity


DAY 2
------------------------------------------------------------
Morning:
- Activity

Afternoon:
- Activity

Evening:
- Activity


Continue until DAY {days}.


============================================================
AI TRIP SUMMARY
============================================================

Best experience:
...

Budget advice:
...

Transport advice:
...

Hotel advice:
...

Important note:
Prices and availability should be verified before booking.
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        print(
            "\n🤖 GENERATING AI ITINERARY..."
        )

        response = model.generate_content(
            prompt
        )


        # ----------------------------------------------------
        # CHECK RESPONSE
        # ----------------------------------------------------

        if response is None:

            return (
                "❌ Gemini returned no response."
            )


        if not hasattr(
            response,
            "text"
        ):

            return (
                "❌ Gemini response "
                "does not contain text."
            )


        text = response.text


        if not text:

            return (
                "❌ Gemini returned "
                "an empty response."
            )


        return text.strip()


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print(
            "\n❌ Gemini itinerary "
            "generation error:"
        )

        print(e)


        return (
            "❌ Unable to generate "
            "AI itinerary.\n"
            f"Error: {e}"
        )