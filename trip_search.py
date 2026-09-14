# ============================================================
# TRIPPILOT - COMPLETE TRIP SEARCH
# ============================================================

from flight import search_flight
from train import search_trains, get_station_code
from bus import search_bus
from hotel import search_hotels
from places import search_places


# ============================================================
# FLIGHTS
# ============================================================

def get_flights(origin, destination):

    print("\n" + "=" * 70)
    print("✈️ SEARCHING FLIGHTS")
    print("=" * 70)

    print(f"✈️ Route: {origin} → {destination}")

    try:

        # Send CITY NAMES directly.
        # flight.py converts:
        # Goa -> GOI
        # Delhi -> DEL
        # Mumbai -> BOM
        # Dehradun -> DED

        flights = search_flight(
            origin,
            destination
        )

        return flights or []

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

    print(
        f"🚆 Route: {origin} → {destination}"
    )

    try:

        # train.py already accepts city names

        origin_code = get_station_code(origin)
        destination_code = get_station_code(destination)

        if not origin_code:

            print(
                f"⚠️ Railway station code not found "
                f"for: {origin}"
            )

            return []

        if not destination_code:

            print(
                f"⚠️ Railway station code not found "
                f"for: {destination}"
            )

            return []

        print(
            f"🚆 Station Route: "
            f"{origin_code} → {destination_code}"
        )

        trains = search_trains(
            origin_code,
            destination_code,
            travel_date
        )

        return trains or []

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

    print(
        f"🚌 Route: {origin} → {destination}"
    )

    try:

        # bus.py accepts city names directly

        buses = search_bus(
            source=origin,
            destination=destination,
            travel_date=travel_date
        )

        return buses or []

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

    print(
        f"🏨 Destination: {destination}"
    )

    print(
        f"💰 Budget per night: ₹{hotel_budget}"
    )

    try:

        # hotel.py receives CITY NAME directly

        hotels = search_hotels(
            destination,
            hotel_budget
        )

        if not hotels:

            print(
                "⚠️ No hotels found."
            )

            return []

        print(
            f"✅ Hotels received: {len(hotels)}"
        )

        # Print first few results for debugging

        for i, hotel in enumerate(
            hotels[:5],
            1
        ):

            print(
                f"\n🏨 Hotel {i}:"
            )

            print(
                "Name:",
                hotel.get(
                    "name",
                    "N/A"
                )
            )

            print(
                "Price:",
                hotel.get(
                    "price",
                    hotel.get(
                        "price_per_night",
                        "N/A"
                    )
                )
            )

            print(
                "Rating:",
                hotel.get(
                    "rating",
                    "N/A"
                )
            )

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

    print(
        f"📍 Destination: {destination}"
    )

    print(
        f"🎯 Interest: {interests}"
    )

    try:

        # places.py receives city name

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
            f"✅ Places found: {len(places)}"
        )

        return places

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
    print("🚀 TRIPPILOT COMPLETE TRIP SEARCH")
    print("=" * 70)

    print(
        f"📍 Route: {origin} → {destination}"
    )

    print(
        f"📅 Travel Date: {travel_date}"
    )

    print(
        f"💰 Hotel Budget: ₹{hotel_budget}"
    )

    print(
        f"🎯 Interests: {interests}"
    )


    # ========================================================
    # FLIGHTS
    # ========================================================

    flights = get_flights(
        origin,
        destination
    )


    # ========================================================
    # TRAINS
    # ========================================================

    trains = get_trains(
        origin,
        destination,
        travel_date
    )


    # ========================================================
    # BUSES
    # ========================================================

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


    # ========================================================
    # DEBUG SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("📊 SEARCH RESULTS")
    print("=" * 70)

    print(
        f"✈️ Flights : {len(flights)}"
    )

    print(
        f"🚆 Trains  : {len(trains)}"
    )

    print(
        f"🚌 Buses   : {len(buses)}"
    )

    print(
        f"🏨 Hotels  : {len(hotels)}"
    )

    print(
        f"📍 Places  : {len(places)}"
    )

    print("=" * 70)


    return trip_data


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(trip_data):

    print("\n")

    print("=" * 70)
    print("📊 TRIPPILOT SEARCH SUMMARY")
    print("=" * 70)


    # ========================================================
    # ROUTE
    # ========================================================

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
        f"📅 Date: {travel_date}"
    )


    # ========================================================
    # TRANSPORT
    # ========================================================

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
        f"✈️ Flights : {len(flights)}"
    )

    print(
        f"🚆 Trains  : {len(trains)}"
    )

    print(
        f"🚌 Buses   : {len(buses)}"
    )


    # ========================================================
    # HOTELS
    # ========================================================

    hotels = trip_data.get(
        "hotels",
        []
    )


    print("\n🏨 HOTELS")

    print(
        f"Hotels found: {len(hotels)}"
    )


    for i, hotel in enumerate(
        hotels[:5],
        1
    ):

        print(
            f"\n🏨 {i}. "
            f"{hotel.get('name', 'N/A')}"
        )

        print(
            "   Price:",
            hotel.get(
                "price",
                hotel.get(
                    "price_per_night",
                    "N/A"
                )
            )
        )

        print(
            "   Rating:",
            hotel.get(
                "rating",
                "N/A"
            )
        )


    # ========================================================
    # PLACES
    # ========================================================

    places = trip_data.get(
        "places",
        []
    )


    print("\n📍 PLACES")

    print(
        f"Places found: {len(places)}"
    )


    print("\n" + "=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n🚀 TripPilot")
    print("=" * 50)


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

    print("=" * 70)
    print("✅ TRIP SEARCH COMPLETED")
    print("=" * 70)