# ============================================================
# TRIPPILOT - COMPLETE TRIP SEARCH
# ============================================================

from flight import search_flight
from train import search_trains, get_station_code
from bus import search_bus
from hotel import search_hotels
from places import search_places


# ============================================================
# AIRPORT MAPPING
# ============================================================

AIRPORT_CODES = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "dehradun": "DED",
    "goa": "GOI",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU",
    "pune": "PNQ",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "ahmedabad": "AMD",
    "amritsar": "ATQ",
    "varanasi": "VNS",
}


# ============================================================
# FLIGHTS
# ============================================================

def get_flights(origin, destination):
    print("\n" + "=" * 70)
    print("✈️ SEARCHING FLIGHTS")
    print("=" * 70)

    origin_code = AIRPORT_CODES.get(origin.lower())
    destination_code = AIRPORT_CODES.get(destination.lower())

    if not origin_code or not destination_code:
        print("⚠️ Airport code not available.")
        return []

    try:
        flights = search_flight(
            origin_code,
            destination_code
        )

        return flights if flights else []

    except Exception as e:
        print("\n❌ Flight search failed:")
        print(e)
        return []


# ============================================================
# TRAINS
# ============================================================

def get_trains(origin, destination, travel_date):
    print("\n" + "=" * 70)
    print("🚆 SEARCHING TRAINS")
    print("=" * 70)

    try:
        origin_code = get_station_code(origin)

        destination_code = get_station_code(destination)

        if not origin_code:
            print(f"⚠️ Station code not found for {origin}")
            return []

        if not destination_code:
            print(f"⚠️ Station code not found for {destination}")
            return []

        trains = search_trains(
            origin_code,
            destination_code,
            travel_date
        )

        return trains if trains else []

    except Exception as e:
        print("\n❌ Train search failed:")
        print(e)
        return []


# ============================================================
# BUSES
# ============================================================

def get_buses(origin, destination, travel_date):
    print("\n" + "=" * 70)
    print("🚌 SEARCHING BUSES")
    print("=" * 70)

    try:
        buses = search_bus(
            origin,
            destination,
            travel_date
        )

        return buses if buses else []

    except Exception as e:
        print("\n❌ Bus search failed:")
        print(e)
        return []


# ============================================================
# HOTELS
# ============================================================

def get_hotels(destination, hotel_budget):
    print("\n" + "=" * 70)
    print("🏨 SEARCHING HOTELS")
    print("=" * 70)

    try:
        hotels = search_hotels(
            destination,
            hotel_budget
        )

        if not hotels:
            print("⚠️ No hotels found.")
            return []

        print(f"✅ Hotels received: {len(hotels)}")

        return hotels

    except Exception as e:
        print("\n❌ Hotel search failed:")
        print(e)
        return []


# ============================================================
# PLACES
# ============================================================

def get_places(destination, interests):
    print("\n" + "=" * 70)
    print("📍 SEARCHING PLACES")
    print("=" * 70)

    try:
        places = search_places(
            destination,
            interests
        )

        return places if places else []

    except Exception as e:
        print("\n❌ Places search failed:")
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
    print("🌍 TRIPPILOT - COMPLETE TRIP SEARCH")
    print("=" * 70)

    print(f"📍 From        : {origin}")
    print(f"📍 Destination : {destination}")
    print(f"📅 Date        : {travel_date}")
    print(f"🏨 Hotel Budget: ₹{hotel_budget}")
    print(f"🎯 Interests   : {interests}")

    # --------------------------------------------------------
    # TRANSPORT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # HOTELS
    # --------------------------------------------------------

    hotels = get_hotels(
        destination,
        hotel_budget
    )

    # --------------------------------------------------------
    # PLACES
    # --------------------------------------------------------

    places = get_places(
        destination,
        interests
    )

    # --------------------------------------------------------
    # FINAL DATA
    # --------------------------------------------------------

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

def display_summary(trip_data):

    print("\n")
    print("=" * 70)
    print("📊 TRIP SEARCH SUMMARY")
    print("=" * 70)

    route = trip_data.get("route", {})

    transport = trip_data.get(
        "transport",
        {}
    )

    hotels = trip_data.get(
        "hotels",
        []
    )

    places = trip_data.get(
        "places",
        []
    )

    print(
        f"\n📍 Route: "
        f"{route.get('origin')} → "
        f"{route.get('destination')}"
    )

    print(
        f"📅 Date: "
        f"{route.get('travel_date')}"
    )

    print("\n🚗 TRANSPORT")

    print(
        f"✈️ Flights : "
        f"{len(transport.get('flights', []))}"
    )

    print(
        f"🚆 Trains  : "
        f"{len(transport.get('trains', []))}"
    )

    print(
        f"🚌 Buses   : "
        f"{len(transport.get('buses', []))}"
    )

    print("\n🏨 HOTELS")

    print(
        f"Hotels found: "
        f"{len(hotels)}"
    )

    print("\n📍 PLACES")

    print(
        f"Places found: "
        f"{len(places)}"
    )

    print("\n" + "=" * 70)
    print("✅ TRIP SEARCH COMPLETED")
    print("=" * 70)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    origin = input(
        "Starting city: "
    ).strip()

    destination = input(
        "Destination: "
    ).strip()

    travel_date = input(
        "Travel date (YYYY-MM-DD): "
    ).strip()

    hotel_budget = int(
        input(
            "Hotel budget per night (₹): "
        ).strip()
    )

    interests = input(
        "Interests (e.g. beaches, adventure, nature): "
    ).strip()

    trip_data = search_trip(
        origin=origin,
        destination=destination,
        travel_date=travel_date,
        hotel_budget=hotel_budget,
        interests=interests
    )

    display_summary(trip_data)