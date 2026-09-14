# ============================================================
# TRIPPILOT - AI ITINERARY GENERATOR
# ============================================================

import os
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# ------------------------------------------------------------
# LLM
# ------------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)


# ------------------------------------------------------------
# PROMPT
# ------------------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are TripPilot, an intelligent AI travel planner.

Your job is to create a realistic, practical and personalized
travel itinerary.

Rules:

1. Use ONLY the places provided by the application.
2. Do not invent attractions.
3. Consider the user's interests.
4. Consider the number of travel days.
5. Group nearby places together when possible.
6. Avoid putting too many places in one day.
7. Include morning, afternoon and evening plans where possible.
8. Keep the plan practical.
9. Consider the user's budget.
10. Mention if the estimated trip cost exceeds the budget.
11. Give useful travel suggestions.
12. Return ONLY valid JSON.
"""
    ),
    (
        "human",
        """
Create a travel plan using the following information.

Starting city:
{source}

Destination:
{destination}

Travel date:
{travel_date}

Number of days:
{days}

Total budget:
₹{budget}

Interests:
{interests}

Transport options:
{transport_options}

Available hotels:
{hotels}

Available places:
{places}

Return JSON using EXACTLY this structure:

{{
    "summary": "short trip summary",

    "recommended_transport": {{
        "type": "Bus/Train/Flight",
        "price": 0,
        "reason": "why this option is recommended"
    }},

    "hotel": {{
        "name": "hotel name",
        "location": "hotel location",
        "price_per_night": 0,
        "total_cost": 0
    }},

    "itinerary": [
        {{
            "day": 1,
            "morning": "activity",
            "afternoon": "activity",
            "evening": "activity"
        }}
    ],

    "cost_breakdown": {{
        "transport": 0,
        "hotel": 0,
        "food": 0,
        "local_transport": 0,
        "total": 0,
        "budget_remaining": 0
    }},

    "budget_status": "Within budget / Exceeds budget",

    "tips": [
        "tip 1",
        "tip 2",
        "tip 3"
    ]
}}
"""
    )
])


# ------------------------------------------------------------
# GENERATE PLAN
# ------------------------------------------------------------

def generate_ai_plan(
    source,
    destination,
    travel_date,
    days,
    budget,
    interests,
    transport_options,
    hotels,
    places
):

    try:

        chain = prompt | llm

        response = chain.invoke({
            "source": source,
            "destination": destination,
            "travel_date": travel_date,
            "days": days,
            "budget": budget,
            "interests": interests,

            "transport_options": json.dumps(
                transport_options,
                indent=2,
                ensure_ascii=False
            ),

            "hotels": json.dumps(
                hotels,
                indent=2,
                ensure_ascii=False
            ),

            "places": json.dumps(
                places,
                indent=2,
                ensure_ascii=False
            )
        })

        content = response.content

        # ----------------------------------------------------
        # Gemini sometimes returns markdown JSON
        # ----------------------------------------------------

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):
                    text_parts.append(
                        item.get("text", "")
                    )

                else:
                    text_parts.append(str(item))

            content = "".join(text_parts)

        content = str(content).strip()

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # ----------------------------------------------------
        # Convert JSON
        # ----------------------------------------------------

        plan = json.loads(content)

        return plan

    except json.JSONDecodeError as e:

        print("\n❌ LLM returned invalid JSON.")
        print("Error:", e)

        return None

    except Exception as e:

        print("\n❌ AI planner error:")
        print(e)

        return None