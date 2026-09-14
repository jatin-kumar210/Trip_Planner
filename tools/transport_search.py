# ============================================================
# TRIPPILOT - ALL TRANSPORT SEARCH
# ============================================================

from train import find_station, search_train
from flight import search_flight


# ============================================================
# CITY → AIRPORT CODE
# ============================================================

AIRPORT_CODES = {

    "delhi": "DEL",
    "new delhi": "DEL",

    "dehradun": "DED",

    "mumbai": "BOM",

    "pune": "PNQ",

    "bangalore": "BLR",
    "bengaluru": "BLR",

    "hyderabad": "HYD",

    "chennai": "MAA",

    "kolkata": "CCU",

    "ahmedabad": "AMD",

    "jaipur": "JAI",

    "goa": "GOI",

    "lucknow": "LKO",

    "varanasi": "VNS",

    "amritsar": "ATQ",

    "chandigarh": "IXC",

    "patna": "PAT",

    "bhopal": "BHO",

    "indore": "IDR",
}


# ============================================================
# GET AIRPORT CODE
# ============================================================

def get_airport_code(city):

    city = city.strip().lower()

    return AIRPORT_CODES.get(city)


# ============================================================
# SEARCH ALL TRANSPORT
# ============================================================

def search_all_transport(
    source,
    destination,
    travel_date
):

    print("\n" + "=" * 70)
    print("🔍 SEARCHING TRANSPORT OPTIONS")
    print("=" * 70)

    print(
        f"\n📍 Route : "
        f"{source} → {destination}"
    )

    print(
        f"📅 Date  : "
        f"{travel_date}"
    )

    results = {

        "train": [],

        "flight": [],

        "bus": []
    }


    # ========================================================
    # TRAIN
    # ========================================================

    print("\n🚆 TRAIN SEARCH")
    print("-" * 70)

    try:

        source_station = find_station(
            source
        )

        destination_station = find_station(
            destination
        )

        if (
            source_station
            and destination_station
            and source_station.get("code")
            and destination_station.get("code")
        ):

            trains = search_train(

                source_station["code"],

                destination_station["code"],

                travel_date
            )

            results["train"] = trains

        else:

            print(
                "⚠️ Railway station "
                "could not be resolved."
            )

    except Exception as e:

        print(
            "⚠️ Train search error:"
        )

        print(e)


    # ========================================================
    # FLIGHT
    # ========================================================

    print("\n✈️ FLIGHT SEARCH")
    print("-" * 70)

    try:

        origin_code = get_airport_code(
            source
        )

        destination_code = get_airport_code(
            destination
        )

        if (
            origin_code
            and destination_code
        ):

            flights = search_flight(

                origin_code,

                destination_code
            )

            results["flight"] = flights

        else:

            print(
                "⚠️ Airport code unavailable."
            )

    except Exception as e:

        print(
            "⚠️ Flight search error:"
        )

        print(e)


    # ========================================================
    # BUS
    # ========================================================

    print("\n🚌 BUS SEARCH")
    print("-" * 70)

    print(
        "ℹ️ Bus search requires "
        "provider-specific source/destination IDs."
    )

    print(
        "⚠️ Bus search skipped for now."
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("💰 TRANSPORT SEARCH SUMMARY")
    print("=" * 70)

    print(
        f"🚆 Trains found  : "
        f"{len(results['train'])}"
    )

    print(
        f"✈️ Flights found : "
        f"{len(results['flight'])}"
    )

    print(
        f"🚌 Buses found   : "
        f"{len(results['bus'])}"
    )

    return results