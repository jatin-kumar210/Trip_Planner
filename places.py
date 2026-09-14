# ============================================================
# TRIPPILOT - PLACES SEARCH
# ============================================================

import os
import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)


TAVILY_URL = (
    "https://api.tavily.com/search"
)


# ============================================================
# SEARCH PLACES
# ============================================================

def search_places(
    destination,
    interests
):

    print("\n" + "=" * 70)

    print(
        "📍 FINDING DESTINATION PLACES"
    )

    print("=" * 70)

    print(
        f"🔎 Destination: "
        f"{destination}"
    )

    print(
        f"🎯 Interest: "
        f"{interests}"
    )


    if not TAVILY_API_KEY:

        print(
            "\n❌ TAVILY_API_KEY not found."
        )

        print(
            "Add TAVILY_API_KEY to .env"
        )

        return []


    # ========================================================
    # SEARCH QUERY
    # ========================================================

    query = (
        f"best tourist attractions in "
        f"{destination} India "
        f"places to visit "
        f"{interests}"
    )


    print("\n🔍 Searching places...")

    print(
        f"Query: {query}"
    )


    payload = {

        "api_key": TAVILY_API_KEY,

        "query": query,

        "search_depth": "advanced",

        "include_answer": False,

        "include_raw_content": False,

        "max_results": 10
    }


    try:

        response = requests.post(
            TAVILY_URL,
            json=payload,
            timeout=30
        )


        if response.status_code != 200:

            print(
                f"\n❌ Tavily error: "
                f"{response.status_code}"
            )

            print(
                response.text
            )

            return []


        data = response.json()


        results = data.get(
            "results",
            []
        )


        if not results:

            print(
                "\n❌ No places found."
            )

            return []


        places = []


        # ====================================================
        # PROCESS RESULTS
        # ====================================================

        for result in results:

            title = result.get(
                "title",
                ""
            ).strip()


            content = result.get(
                "content",
                ""
            ).strip()


            url = result.get(
                "url",
                ""
            )


            if not title:

                continue


            # ------------------------------------------------
            # DESTINATION SAFETY FILTER
            # ------------------------------------------------

            destination_lower = (
                destination.lower()
            )

            title_lower = (
                title.lower()
            )

            content_lower = (
                content.lower()
            )


            combined_text = (
                title_lower
                + " "
                + content_lower
            )


            # ------------------------------------------------
            # Avoid obviously unrelated results
            # ------------------------------------------------

            if (
                destination_lower
                not in combined_text
            ):

                continue


            place = {

                "name": title,

                "location": destination,

                "type": interests,

                "description": content,

                "url": url
            }


            places.append(
                place
            )


        print(
            f"\n✅ Places found: "
            f"{len(places)}"
        )


        return places


    except requests.exceptions.RequestException as e:

        print(
            "\n❌ Places network error:"
        )

        print(e)

        return []


    except Exception as e:

        print(
            "\n❌ Places search error:"
        )

        print(e)

        return []


# ============================================================
# FORMAT PLACES FOR GEMINI
# ============================================================

def format_places(
    places
):

    if not places:

        return (
            "No destination places "
            "were found."
        )


    output = []


    for i, place in enumerate(
        places[:30],
        1
    ):

        name = place.get(
            "name",
            "Unknown"
        )


        location = place.get(
            "location",
            "Unknown"
        )


        place_type = place.get(
            "type",
            "Attraction"
        )


        description = place.get(
            "description",
            ""
        )


        url = place.get(
            "url",
            ""
        )


        output.append(

            f"{i}. {name}\n"
            f"   Location: {location}\n"
            f"   Type: {place_type}\n"
            f"   Description: {description[:500]}\n"
            f"   Source: {url}\n"
        )


    return "\n".join(
        output
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    destination = input(
        "Destination: "
    ).strip()


    interests = input(
        "Interest: "
    ).strip()


    places = search_places(
        destination,
        interests
    )


    print("\n" + "=" * 70)

    print(
        "📍 PLACES RESULTS"
    )

    print("=" * 70)


    print(
        format_places(
            places
        )
    )