# ============================================================
# TRIPPILOT - FLIGHT SEARCH
# CITY NAME INPUT
# ============================================================

from tools.flight_api import search_flights


# ============================================================
# CITY -> AIRPORT CODE
# ============================================================

CITY_AIRPORTS = {

    # Uttarakhand
    "dehradun": "DED",

    # Delhi
    "delhi": "DEL",
    "new delhi": "DEL",

    # Maharashtra
    "mumbai": "BOM",
    "bombay": "BOM",
    "pune": "PNQ",
    "nagpur": "NAG",

    # Goa
    "goa": "GOI",
    "madgaon": "GOI",
    "mopa": "GOX",

    # Karnataka
    "bangalore": "BLR",
    "bengaluru": "BLR",

    # Telangana
    "hyderabad": "HYD",

    # Tamil Nadu
    "chennai": "MAA",

    # West Bengal
    "kolkata": "CCU",
    "calcutta": "CCU",

    # Rajasthan
    "jaipur": "JAI",

    # Uttar Pradesh
    "lucknow": "LKO",
    "varanasi": "VNS",
    "agra": "AGR",

    # Gujarat
    "ahmedabad": "AMD",

    # Kerala
    "kochi": "COK",
    "cochin": "COK",
    "thiruvananthapuram": "TRV",

    # Punjab
    "amritsar": "ATQ",
    "chandigarh": "IXC",

    # Bihar
    "patna": "PAT",

    # Odisha
    "bhubaneswar": "BBI",

    # Madhya Pradesh
    "indore": "IDR",
    "bhopal": "BHO",

    # Jammu & Kashmir
    "srinagar": "SXR",

    # Jharkhand
    "ranchi": "IXR",
}


# ============================================================
# CITY NAME -> IATA CODE
# ============================================================

def get_airport_code(city):

    if not city:
        return None

    city = city.strip().lower()

    # IMPORTANT:
    # Check city FIRST.
    # Therefore "Goa" becomes GOI, NOT GOA.

    if city in CITY_AIRPORTS:
        return CITY_AIRPORTS[city]

    # Optional support if someone directly enters
    # an actual airport code such as DEL or BOM.

    if len(city) == 3 and city.isalpha():
        return city.upper()

    return None


# ============================================================
# SEARCH FLIGHTS
# ============================================================

def search_flight(origin, destination):

    try:

        # ----------------------------------------------------
        # Convert city names into airport codes
        # ----------------------------------------------------

        origin_code = get_airport_code(origin)
        destination_code = get_airport_code(destination)


        # ----------------------------------------------------
        # Validate origin
        # ----------------------------------------------------

        if not origin_code:

            print(
                f"\n❌ Airport not found for: {origin}"
            )

            print(
                "\nPlease enter a supported city name."
            )

            return []


        # ----------------------------------------------------
        # Validate destination
        # ----------------------------------------------------

        if not destination_code:

            print(
                f"\n❌ Airport not found for: {destination}"
            )

            print(
                "\nPlease enter a supported city name."
            )

            return []


        # ----------------------------------------------------
        # Display search information
        # ----------------------------------------------------

        print("\n" + "=" * 65)
        print("✈️ TRIPPILOT FLIGHT SEARCH")
        print("=" * 65)

        print(
            f"📍 From        : "
            f"{origin.title()} ({origin_code})"
        )

        print(
            f"📍 Destination : "
            f"{destination.title()} ({destination_code})"
        )

        print("\n🔍 Searching flights...")


        # ----------------------------------------------------
        # CALL YOUR EXISTING FLIGHT API
        # ----------------------------------------------------

        flights = search_flights(
            origin_code,
            destination_code
        )


        # ----------------------------------------------------
        # NO FLIGHTS
        # ----------------------------------------------------

        if not flights:

            print(
                "\n❌ No flights found for this route."
            )

            return []


        # ----------------------------------------------------
        # FLIGHTS FOUND
        # ----------------------------------------------------

        print(
            f"\n✅ Flights found: {len(flights)}"
        )


        # ----------------------------------------------------
        # DISPLAY FLIGHTS
        # ----------------------------------------------------

        for i, flight in enumerate(flights[:5], 1):

            airline = flight.get(
                "airline",
                {}
            ).get(
                "name",
                "N/A"
            )


            flight_number = flight.get(
                "flight",
                {}
            ).get(
                "iata",
                "N/A"
            )


            departure = flight.get(
                "departure",
                {}
            )


            arrival = flight.get(
                "arrival",
                {}
            )


            print("\n" + "-" * 65)
            print(f"✈️ FLIGHT {i}")
            print("-" * 65)


            print(
                "Airline    :",
                airline
            )


            print(
                "Flight     :",
                flight_number
            )


            print(
                "From       :",
                departure.get(
                    "airport",
                    "N/A"
                )
            )


            print(
                "To         :",
                arrival.get(
                    "airport",
                    "N/A"
                )
            )


            print(
                "Departure  :",
                departure.get(
                    "scheduled",
                    "N/A"
                )
            )


            print(
                "Arrival    :",
                arrival.get(
                    "scheduled",
                    "N/A"
                )
            )


            print(
                "Status     :",
                flight.get(
                    "flight_status",
                    "N/A"
                )
            )


        return flights


    except Exception as e:

        print("\n❌ Flight API error:")
        print(e)

        return []


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n🚀 TripPilot Flight Search")
    print("=" * 65)

    origin = input(
        "Enter departure city: "
    ).strip()


    destination = input(
        "Enter destination city: "
    ).strip()


    print(
        f"\n🔍 Searching: "
        f"{origin.title()} → {destination.title()}"
    )


    search_flight(
        origin,
        destination
    )