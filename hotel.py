import os
import re
from dotenv import load_dotenv
from tavily import TavilyClient


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("❌ TAVILY_API_KEY not found in .env")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# ============================================================
# SEARCH HOTELS
# ============================================================

def search_hotels(destination, budget):

    query = (
        f"hotels in {destination} India "
        f"hotel name location price per night "
        f"under Rs {budget}"
    )

    print("\n🔍 Searching hotels...")
    print("Query:", query)

    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_domains=[
            "oyorooms.com",
            "booking.com",
            "goibibo.com",
            "makemytrip.com",
            "easemytrip.com"
        ]
    )

    return response


# ============================================================
# CHECK IF NAME IS A REAL HOTEL NAME
# ============================================================

def valid_hotel_name(name):

    name = name.strip()

    if not name:
        return False

    # ----------------------------------------
    # Length check
    # ----------------------------------------

    if len(name) > 120:
        return False

    # ----------------------------------------
    # Things that are NOT hotel names
    # ----------------------------------------

    invalid_phrases = [
        "popular hotel destinations",
        "hotel destinations",
        "popular destinations",
        "cheap hotel in",
        "hotels in ",
        "hotel in ",
        "best hotels",
        "budget hotels",
        "hotel results",
        "how much",
        "we make it",
        "login",
        "about us",
        "privacy policy",
        "terms and conditions",
        "guest policies",
        "download",
        "call for",
        "hotels near me",
        "travel guide",
        "official oyo blog",
        "popular hotel",
    ]

    name_lower = name.lower()

    for phrase in invalid_phrases:

        if phrase in name_lower:
            return False

    # ----------------------------------------
    # Must contain hotel-like keyword
    # ----------------------------------------

    hotel_keywords = [
        "oyo ",
        "hotel ",
        "resort ",
        "guest house",
        "guesthouse",
        "villa ",
        "inn ",
        "hostel",
        "suites",
        "homestay",
        "home stay"
    ]

    if not any(
        keyword in name_lower
        for keyword in hotel_keywords
    ):
        return False

    # ----------------------------------------
    # Reject names containing webpage garbage
    # ----------------------------------------

    garbage = [
        "₹",
        "ratings",
        "taxes",
        "privacy",
        "copyright",
        "http",
        "www.",
        "login",
        "sign up",
        "fabulous",
        "excellent",
        "very good"
    ]

    for word in garbage:

        if word in name_lower:
            return False

    return True


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(section):

    lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip()
    ]

    for line in lines:

        # Location usually contains Goa / India
        if re.search(
            r"\bGoa\b",
            line,
            re.IGNORECASE
        ):

            # Ignore lines that are clearly not locations
            if not any(
                word in line.lower()
                for word in [
                    "₹",
                    "rating",
                    "facility",
                    "wifi",
                    "parking",
                    "breakfast",
                    "taxes"
                ]
            ):

                return line

    # OYO pages sometimes have "Near ..."
    for line in lines:

        if line.lower().startswith("near "):

            return line

    return "Not available"


# ============================================================
# EXTRACT PRICE
# ============================================================

def extract_price(section):

    # Look for price immediately before taxes
    match = re.search(
        r"₹\s*([\d,]+)"
        r"(?:₹[\d,]+%?\s*off)?"
        r"\s*\+\s*₹",
        section,
        re.IGNORECASE
    )

    if match:

        try:
            return int(
                match.group(1).replace(",", "")
            )
        except ValueError:
            pass

    # Fallback
    matches = re.findall(
        r"₹\s*([\d,]+)",
        section
    )

    if matches:

        for value in matches:

            price = int(
                value.replace(",", "")
            )

            # Ignore obviously unrealistic values
            if 100 <= price <= 100000:
                return price

    return None


# ============================================================
# EXTRACT TAX
# ============================================================

def extract_taxes(section):

    match = re.search(
        r"\+\s*₹\s*([\d,]+)\s*taxes",
        section,
        re.IGNORECASE
    )

    if match:

        try:
            return int(
                match.group(1).replace(",", "")
            )
        except ValueError:
            pass

    return None


# ============================================================
# EXTRACT RATING
# ============================================================

def extract_rating(section):

    patterns = [
        r"(\d+(?:\.\d+)?)\s*\((\d+)\s*Ratings?\)",
        r"(\d+(?:\.\d+)?)\s*\((\d+)\s*reviews?\)",
        r"(\d+(?:\.\d+)?)\s*/\s*10"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            section,
            re.IGNORECASE
        )

        if match:

            try:
                return float(match.group(1))
            except ValueError:
                pass

    return None


# ============================================================
# EXTRACT OYO HOTELS
# ============================================================

def extract_hotels_from_result(result):

    content = result.get(
        "content",
        ""
    )

    source = result.get(
        "title",
        ""
    )

    url = result.get(
        "url",
        ""
    )

    hotels = []

    # --------------------------------------------------------
    # Split content using markdown headings
    # --------------------------------------------------------

    sections = re.split(
        r"\n?###\s+",
        content
    )

    for section in sections:

        lines = [
            line.strip()
            for line in section.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        # First line is usually hotel name
        name = lines[0]

        # ----------------------------------------------------
        # Clean repeated heading text
        # ----------------------------------------------------

        name = re.sub(
            r"\s+",
            " ",
            name
        ).strip()

        # ----------------------------------------------------
        # Validate hotel name
        # ----------------------------------------------------

        if not valid_hotel_name(name):
            continue

        # ----------------------------------------------------
        # Extract information
        # ----------------------------------------------------

        location = extract_location(section)

        price = extract_price(section)

        taxes = extract_taxes(section)

        rating = extract_rating(section)

        hotel = {
            "name": name,
            "location": location,
            "price": price,
            "taxes": taxes,
            "rating": rating,
            "source": source,
            "url": url
        }

        hotels.append(hotel)

    return hotels


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(hotels):

    unique_hotels = {}

    for hotel in hotels:

        name = hotel["name"].strip().lower()

        if name not in unique_hotels:

            unique_hotels[name] = hotel

        else:

            # Keep the version that has more information
            old = unique_hotels[name]

            if (
                old["price"] is None
                and hotel["price"] is not None
            ):

                unique_hotels[name] = hotel

    return list(
        unique_hotels.values()
    )


# ============================================================
# FILTER BY BUDGET
# ============================================================

def filter_by_budget(hotels, budget):

    filtered = []

    for hotel in hotels:

        price = hotel["price"]

        if price is None:
            continue

        if price <= budget:

            filtered.append(hotel)

    return filtered


# ============================================================
# SORT BY PRICE
# ============================================================

def sort_by_price(hotels):

    return sorted(
        hotels,
        key=lambda hotel: (
            hotel["price"] is None,
            hotel["price"]
            if hotel["price"] is not None
            else 999999
        )
    )


# ============================================================
# DISPLAY HOTELS
# ============================================================

def display_hotels(hotels):

    print("\n")
    print("=" * 70)
    print("🏨 CLEAN HOTEL RESULTS")
    print("=" * 70)

    if not hotels:

        print(
            "\n❌ No reliable hotels found."
        )

        return

    for index, hotel in enumerate(
        hotels,
        start=1
    ):

        print(
            f"\n🏨 HOTEL {index}"
        )

        print("-" * 70)

        print(
            "Name     :",
            hotel["name"]
        )

        print(
            "Location :",
            hotel["location"]
        )

        if hotel["price"] is not None:

            print(
                "Price    : ₹",
                hotel["price"]
            )

        else:

            print(
                "Price    : Not available"
            )

        if hotel["taxes"] is not None:

            print(
                "Taxes    : ₹",
                hotel["taxes"]
            )

        else:

            print(
                "Taxes    : Not available"
            )

        if hotel["rating"] is not None:

            print(
                "Rating   :",
                hotel["rating"]
            )

        else:

            print(
                "Rating   : Not available"
            )

        print(
            "Source   :",
            hotel["source"]
        )

        print(
            "URL      :",
            hotel["url"]
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "🏨 TRIPPILOT"
    )

    print(
        "HOTEL SEARCH SYSTEM"
    )

    print(
        "=" * 70
    )

    destination = input(
        "Enter destination: "
    ).strip()

    if not destination:

        print(
            "❌ Destination cannot be empty."
        )

        return

    budget_input = input(
        "Maximum budget per night: "
    ).strip()

    try:

        budget = int(
            budget_input
        )

    except ValueError:

        print(
            "❌ Please enter a valid number."
        )

        return

    print(
        "\n🔍 Starting hotel search..."
    )

    # --------------------------------------------------------
    # Tavily
    # --------------------------------------------------------

    try:

        results = search_hotels(
            destination,
            budget
        )

    except Exception as e:

        print(
            "\n❌ Tavily error:"
        )

        print(e)

        return

    print(
        "\n✅ Tavily search completed!"
    )

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    all_hotels = []

    for result in results.get(
        "results",
        []
    ):

        hotels = extract_hotels_from_result(
            result
        )

        all_hotels.extend(
            hotels
        )

    print(
        f"📊 Raw hotel entries found: {len(all_hotels)}"
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    all_hotels = remove_duplicates(
        all_hotels
    )

    print(
        f"🧹 After duplicate removal: {len(all_hotels)}"
    )

    # --------------------------------------------------------
    # Budget filter
    # --------------------------------------------------------

    all_hotels = filter_by_budget(
        all_hotels,
        budget
    )

    print(
        f"💰 Within ₹{budget}: {len(all_hotels)}"
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    all_hotels = sort_by_price(
        all_hotels
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    display_hotels(
        all_hotels
    )

    print("\n")
    print("=" * 70)
    print("✅ Hotel search finished")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()