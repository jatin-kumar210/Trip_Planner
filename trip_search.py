# ============================================================
# TRIPPILOT - COMPLETE TRIP SEARCH
# ============================================================

from flight import search_flight

from train import (
    search_trains,
    get_station_code
)

from bus import search_bus

from hotel import (
    search_hotels,
    extract_hotels_from_result,
    remove_duplicates,
    filter_by_budget,
    sort_by_price
)

from places import search_places


# ============================================================
# AIRPORT CODES
# ============================================================

AIRPORT_CODES = {

    "dehradun": "DED",

    "delhi": "DEL",
    "new delhi": "DEL",

    "mumbai": "BOM",

    "goa": "GOI",
    "madgaon": "GOI",

    "pune": "PNQ",

    "ahmedabad": "AMD",

    "jaipur": "JAI",

    "lucknow": "LKO",

    "varanasi": "VNS",

    "kolkata": "CCU",

    "patna": "PAT",

    "bhopal": "BHO",

    "indore": "IDR",

    "amritsar": "ATQ",

    "chandigarh": "IXC",

    "agra": "AGR",

    "kanpur": "KNU"
}


# ============================================================
# GET AIRPORT CODE
# ============================================================

def get_airport_code(city):

    if not city:
        return None

    city = str(city).lower().strip()

    return AIRPORT_CODES.get(city)


# ============================================================
# FLIGHTS
# ============================================================

def get_flights(
    origin,
    destination
):

    print("\n" + "=" * 70)
    print("✈️ SEARCHING FLIGHTS")
    print("=" * 70)

    origin_code = get_airport_code(
        origin
    )

    destination_code = get_airport_code(
        destination
    )

    if not origin_code:

        print(
            f"⚠️ Airport code not found for: "
            f"{origin}"
        )

        return []

    if not destination_code:

        print(
            f"⚠️ Airport code not found for: "
            f"{destination}"
        )

        return []

    print(
        f"✈️ Route: "
        f"{origin_code} → {destination_code}"
    )

    try:

        flights = search_flight(
            origin_code,
            destination_code
        )

        if not flights:

            print(
                "⚠️ No flights found."
            )

            return []

        print(
            f"✅ Flights received: "
            f"{len(flights)}"
        )

        return flights

    except Exception as e:

        print(
            "\n❌ Flight search failed:"
        )

        print(e)

        return []


# ============================================================
# TRAINS
# ============================================================

def get_trains(
    origin,
    destination,
    travel_date
):

    print("\n" + "=" * 70)
    print("🚆 SEARCHING TRAINS")
    print("=" * 70)

    origin_code = get_station_code(
        origin
    )

    destination_code = get_station_code(
        destination
    )

    if not origin_code:

        print(
            f"⚠️ Railway station code "
            f"not found for: {origin}"
        )

        return []

    if not destination_code:

        print(
            f"⚠️ Railway station code "
            f"not found for: {destination}"
        )

        return []

    print(
        f"🚆 Route: "
        f"{origin_code} → {destination_code}"
    )

    try:

        trains = search_trains(
            origin_code,
            destination_code,
            travel_date
        )

        if not trains:

            print(
                "⚠️ No trains found."
            )

            return []

        print(
            f"✅ Trains received: "
            f"{len(trains)}"
        )

        return trains

    except Exception as e:

        print(
            "\n❌ Train search failed:"
        )

        print(e)

        return []


# ============================================================
# BUSES
# ============================================================

def get_buses(
    origin,
    destination,
    travel_date
):

    print("\n" + "=" * 70)
    print("🚌 SEARCHING BUSES")
    print("=" * 70)

    try:

        buses = search_bus(
            source=origin,
            destination=destination,
            travel_date=travel_date
        )

        if not buses:

            print(
                "⚠️ No buses found."
            )

            return []

        print(
            f"✅ Buses received: "
            f"{len(buses)}"
        )

        return buses

    except Exception as e:

        print(
            "\n❌ Bus search failed:"
        )

        print(e)

        return []


# ============================================================
# HOTEL SEARCH + CLEANING
# ============================================================

def get_hotels(
    destination,
    hotel_budget
):

    print("\n" + "=" * 70)
    print("🏨 SEARCHING HOTELS")
    print("=" * 70)

    print(
        f"🏨 Destination: {destination}"
    )

    print(
        f"💰 Budget per night: ₹{hotel_budget}"
    )

    try:

        # ----------------------------------------------------
        # STEP 1
        # Tavily hotel search
        # ----------------------------------------------------

        raw_response = search_hotels(
            destination,
            hotel_budget
        )

        if not raw_response:

            print(
                "⚠️ No hotel response received."
            )

            return []

        # ----------------------------------------------------
        # IMPORTANT
        #
        # search_hotels() returns a RAW Tavily dictionary.
        #
        # Example:
        #
        # {
        #     "query": "...",
        #     "results": [...]
        # }
        #
        # Never do:
        #
        # raw_response[:5]
        #
        # because raw_response is a dictionary.
        # That causes:
        #
        # slice(None, 5, None)
        # ----------------------------------------------------

        if not isinstance(
            raw_response,
            dict
        ):

            print(
                "⚠️ Unexpected hotel response type:"
            )

            print(
                type(raw_response)
            )

            return []

        raw_results = raw_response.get(
            "results",
            []
        )

        if not isinstance(
            raw_results,
            list
        ):

            print(
                "⚠️ Hotel results are not a list."
            )

            return []

        print(
            f"🔎 Tavily results received: "
            f"{len(raw_results)}"
        )

        # ----------------------------------------------------
        # STEP 2
        # Extract hotels from every Tavily result
        # ----------------------------------------------------

        all_hotels = []

        for result in raw_results:

            if not isinstance(
                result,
                dict
            ):
                continue

            try:

                extracted = (
                    extract_hotels_from_result(
                        result
                    )
                )

                if extracted:

                    all_hotels.extend(
                        extracted
                    )

            except Exception as e:

                print(
                    f"⚠️ Hotel extraction skipped: {e}"
                )

        print(
            f"📊 Raw hotel entries found: "
            f"{len(all_hotels)}"
        )

        if not all_hotels:

            print(
                "⚠️ No valid hotel records extracted."
            )

            return []

        # ----------------------------------------------------
        # STEP 3
        # Remove duplicate hotels
        # ----------------------------------------------------

        try:

            all_hotels = remove_duplicates(
                all_hotels
            )

        except Exception as e:

            print(
                f"⚠️ Duplicate removal skipped: {e}"
            )

        print(
            f"🧹 After duplicate removal: "
            f"{len(all_hotels)}"
        )

        # ----------------------------------------------------
        # STEP 4
        # Filter according to budget
        # ----------------------------------------------------

        try:

            all_hotels = filter_by_budget(
                all_hotels,
                hotel_budget
            )

        except Exception as e:

            print(
                f"⚠️ Budget filtering error: {e}"
            )

            # Safe manual fallback

            filtered = []

            for hotel in all_hotels:

                if not isinstance(
                    hotel,
                    dict
                ):
                    continue

                price = hotel.get(
                    "price"
                )

                if price is None:
                    continue

                try:

                    if float(price) <= float(
                        hotel_budget
                    ):

                        filtered.append(
                            hotel
                        )

                except Exception:

                    continue

            all_hotels = filtered

        print(
            f"💰 Hotels within "
            f"₹{hotel_budget}: "
            f"{len(all_hotels)}"
        )

        # ----------------------------------------------------
        # STEP 5
        # Sort by cheapest price
        # ----------------------------------------------------

        try:

            all_hotels = sort_by_price(
                all_hotels
            )

        except Exception as e:

            print(
                f"⚠️ Sorting error: {e}"
            )

            # Safe manual sort

            def hotel_sort_key(
                hotel
            ):

                if not isinstance(
                    hotel,
                    dict
                ):

                    return (
                        True,
                        float("inf")
                    )

                price = hotel.get(
                    "price"
                )

                try:

                    price = float(
                        price
                    )

                    return (
                        False,
                        price
                    )

                except Exception:

                    return (
                        True,
                        float("inf")
                    )

            all_hotels.sort(
                key=hotel_sort_key
            )

        # ----------------------------------------------------
        # STEP 6
        # Final result
        # ----------------------------------------------------

        print(
            f"✅ Final hotels ready: "
            f"{len(all_hotels)}"
        )

        # Print a small preview safely.
        # IMPORTANT: slicing is done only on a LIST.

        preview = all_hotels[
            :5
        ]

        for index, hotel in enumerate(
            preview,
            start=1
        ):

            if not isinstance(
                hotel,
                dict
            ):
                continue

            print(
                f"\n🏨 HOTEL {index}"
            )

            print(
                "Name     :",
                hotel.get(
                    "name",
                    "N/A"
                )
            )

            print(
                "Location :",
                hotel.get(
                    "location",
                    "N/A"
                )
            )

            print(
                "Price    :",
                hotel.get(
                    "price",
                    "N/A"
                )
            )

            print(
                "Rating   :",
                hotel.get(
                    "rating",
                    "N/A"
                )
            )

        return all_hotels

    except Exception as e:

        print(
            "\n❌ Hotel search failed:"
        )

        print(
            repr(e)
        )

        return []


# ============================================================
# PLACES
# ============================================================

def get_places(
    destination,
    interests
):

    print("\n" + "=" * 70)
    print("📍 SEARCHING PLACES")
    print("=" * 70)

    try:

        places = search_places(
            destination,
            interests
        )

        if not places:

            print(
                "⚠️ No places found."
            )

            return []

        print(
            f"✅ Places received: "
            f"{len(places)}"
        )

        return places

    except Exception as e:

        print(
            "\n❌ Places search failed:"
        )

        print(e)

        return []


# ============================================================
# COMPLETE TRIP SEARCH
# ============================================================

def search_trip(
    origin,
    destination,
    travel_date,
    hotel_budget,
    interests
):

    print("\n")

    print("=" * 70)
    print(
        "🚀 TRIPPILOT COMPLETE TRIP SEARCH"
    )
    print("=" * 70)

    print(
        f"📍 Route: "
        f"{origin} → {destination}"
    )

    print(
        f"📅 Travel Date: "
        f"{travel_date}"
    )

    print(
        f"💰 Hotel Budget: "
        f"₹{hotel_budget}"
    )

    print(
        f"🎯 Interests: "
        f"{interests}"
    )

    # ========================================================
    # TRANSPORT
    # ========================================================

    flights = get_flights(
        origin,
        destination
    )

    trains = get_trains(
        origin,
        destination,
        travel_date
    )

    buses = get_buses(
        origin,
        destination,
        travel_date
    )

    # ========================================================
    # HOTELS
    # ========================================================

    hotels = get_hotels(
        destination,
        hotel_budget
    )

    # ========================================================
    # PLACES
    # ========================================================

    places = get_places(
        destination,
        interests
    )

    # ========================================================
    # FINAL TRIP DATA
    # ========================================================

    trip_data = {

        "route": {

            "origin": origin,

            "destination": destination,

            "travel_date": travel_date

        },

        "transport": {

            "flights": flights,

            "trains": trains,

            "buses": buses

        },

        "hotels": hotels,

        "places": places

    }

    return trip_data


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(
    trip_data
):

    print("\n")

    print("=" * 70)
    print(
        "📊 TRIPPILOT SEARCH SUMMARY"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # ROUTE
    # --------------------------------------------------------

    route = trip_data.get(
        "route",
        {}
    )

    origin = route.get(
        "origin",
        "N/A"
    )

    destination = route.get(
        "destination",
        "N/A"
    )

    travel_date = route.get(
        "travel_date",
        "N/A"
    )

    print(
        f"\n📍 Route: "
        f"{origin} → {destination}"
    )

    print(
        f"📅 Date: "
        f"{travel_date}"
    )

    # --------------------------------------------------------
    # TRANSPORT
    # --------------------------------------------------------

    transport = trip_data.get(
        "transport",
        {}
    )

    flights = transport.get(
        "flights",
        []
    )

    trains = transport.get(
        "trains",
        []
    )

    buses = transport.get(
        "buses",
        []
    )

    print("\n🚗 TRANSPORT")

    print(
        f"✈️ Flights : "
        f"{len(flights)}"
    )

    print(
        f"🚆 Trains  : "
        f"{len(trains)}"
    )

    print(
        f"🚌 Buses   : "
        f"{len(buses)}"
    )

    # --------------------------------------------------------
    # HOTELS
    # --------------------------------------------------------

    hotels = trip_data.get(
        "hotels",
        []
    )

    print("\n🏨 HOTELS")

    print(
        f"Hotels found: "
        f"{len(hotels)}"
    )

    # --------------------------------------------------------
    # PLACES
    # --------------------------------------------------------

    places = trip_data.get(
        "places",
        []
    )

    print("\n📍 PLACES")

    print(
        f"Places found: "
        f"{len(places)}"
    )

    print(
        "\n" + "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n🚀 TripPilot"
    )

    print(
        "=" * 50
    )

    # --------------------------------------------------------
    # USER INPUT
    # --------------------------------------------------------

    origin = input(
        "Enter starting city: "
    ).strip()

    destination = input(
        "Enter destination city: "
    ).strip()

    travel_date = input(
        "Enter travel date (YYYY-MM-DD): "
    ).strip()

    hotel_budget = float(
        input(
            "Enter hotel budget per night: "
        ).strip()
    )

    interests = input(
        "Enter your interests "
        "(nature, adventure, beaches, etc.): "
    ).strip()

    # --------------------------------------------------------
    # SEARCH EVERYTHING
    # --------------------------------------------------------

    trip_data = search_trip(

        origin,

        destination,

        travel_date,

        hotel_budget,

        interests

    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    display_summary(
        trip_data
    )

    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    print("\n")

    print(
        "=" * 70
    )

    print(
        "✅ TRIP SEARCH COMPLETED"
    )

    print(
        "=" * 70
    )