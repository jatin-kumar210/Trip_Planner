import os
import requests
from dotenv import load_dotenv

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

PAY2ALL_API_KEY = os.getenv("PAY2ALL_API_KEY")

BASE_URL = "https://www.pay2all.in/api/v1"

CITY_URL = f"{BASE_URL}/buses/cities"
BUS_SEARCH_URL = f"{BASE_URL}/buses/search"

HEADERS = {
    "Authorization": f"Bearer {PAY2ALL_API_KEY}",
    "x-api-token": PAY2ALL_API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ============================================================
# API KEY
# ============================================================

def check_api_key():

    if not PAY2ALL_API_KEY:
        print("❌ PAY2ALL_API_KEY is missing in .env")
        return False

    return True


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_number(value):

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:

        value = (
            str(value)
            .replace("₹", "")
            .replace(",", "")
            .replace("INR", "")
            .strip()
        )

        if not value:
            return None

        return float(value)

    except (ValueError, TypeError):

        return None


# ============================================================
# NORMALIZE DATE
# ============================================================

def normalize_date(travel_date):

    if not travel_date:
        return None

    travel_date = str(travel_date).strip()

    # YYYY-MM-DD
    if len(travel_date) == 10:

        try:

            year = int(travel_date[0:4])
            month = int(travel_date[5:7])
            day = int(travel_date[8:10])

            if (
                travel_date[4] == "-"
                and travel_date[7] == "-"
                and 1 <= month <= 12
                and 1 <= day <= 31
            ):

                return travel_date

        except ValueError:
            pass

    # Other common formats
    from datetime import datetime

    formats = [
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for fmt in formats:

        try:

            date_obj = datetime.strptime(
                travel_date,
                fmt
            )

            return date_obj.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    return None


# ============================================================
# GET CITY ID
# ============================================================

def get_city_id(city_name):

    if not city_name:
        return None

    if not check_api_key():
        return None

    city_name = str(city_name).strip()

    try:

        response = requests.get(
            CITY_URL,
            headers=HEADERS,
            params={
                "q": city_name
            },
            timeout=30
        )

        print("\n" + "=" * 70)
        print(f"🔎 CITY SEARCH: {city_name}")
        print("=" * 70)

        print(
            "City API Status:",
            response.status_code
        )

        if response.status_code != 200:

            print("\n❌ City API Error:")
            print(response.text)

            return None

        try:

            data = response.json()

        except ValueError:

            print("\n❌ Invalid JSON response:")
            print(response.text)

            return None

        if not isinstance(data, dict):

            print("❌ Unexpected city response.")
            print(data)

            return None

        status_id = data.get(
            "status_id"
        )

        message = data.get(
            "message",
            ""
        )

        if status_id != 1:

            print(
                "❌ Pay2All city API error:",
                message
            )

            return None

        city_data = data.get(
            "data",
            {}
        )

        if not isinstance(city_data, dict):
            return None

        cities = city_data.get(
            "cities",
            []
        )

        if not cities:

            print(
                "⚠️ No cities returned."
            )

            return None

        target = city_name.lower()

        # ----------------------------------------------------
        # EXACT MATCH
        # ----------------------------------------------------

        for city in cities:

            if not isinstance(city, dict):
                continue

            name = str(
                city.get("name", "")
            ).strip()

            city_id = city.get("id")

            if (
                city_id is not None
                and name.lower() == target
            ):

                print(
                    f"✅ {name} ID: {city_id}"
                )

                return city_id

        # ----------------------------------------------------
        # PARTIAL MATCH
        # ----------------------------------------------------

        for city in cities:

            if not isinstance(city, dict):
                continue

            name = str(
                city.get("name", "")
            ).strip()

            city_id = city.get("id")

            if city_id is None:
                continue

            if target in name.lower():

                print(
                    f"✅ Matched {name} ID: {city_id}"
                )

                return city_id

        print(
            f"❌ City not found: {city_name}"
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "❌ City API request timed out."
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            "❌ City API request error:",
            e
        )

        return None

    except Exception as e:

        print(
            "❌ City search error:",
            e
        )

        return None


# ============================================================
# NORMALIZE BUS
# ============================================================

def normalize_bus(bus):

    if not isinstance(bus, dict):
        return None

    fare_min = safe_number(
        bus.get("fare_min")
        if bus.get("fare_min") is not None
        else bus.get("fareMin")
    )

    fare_max = safe_number(
        bus.get("fare_max")
        if bus.get("fare_max") is not None
        else bus.get("fareMax")
    )

    return {

        # ----------------------------------------------------
        # COMMON TYPE
        # ----------------------------------------------------

        "type": "BUS",

        "mode": "Bus",

        # IMPORTANT:
        # Streamlit can directly use this.
        "price": fare_min,

        # ----------------------------------------------------
        # IDs
        # ----------------------------------------------------

        "trip_id": (
            bus.get("trip_id")
            or bus.get("tripId")
            or bus.get("id")
        ),

        # ----------------------------------------------------
        # BASIC INFO
        # ----------------------------------------------------

        "operator": (
            bus.get("operator")
            or "Unknown Operator"
        ),

        "bus_type": (
            bus.get("bus_type")
            or bus.get("busType")
            or "Bus"
        ),

        "departure": (
            bus.get("departure")
            or "N/A"
        ),

        "arrival": (
            bus.get("arrival")
            or "N/A"
        ),

        "duration": (
            bus.get("duration")
            or "N/A"
        ),

        # ----------------------------------------------------
        # FARE
        # ----------------------------------------------------

        "fare_min": fare_min,

        "fare_max": fare_max,

        "fare": (
            f"₹{fare_min:.0f}"
            if fare_min is not None
            else "Fare unavailable"
        ),

        "currency": (
            bus.get("currency")
            or "INR"
        ),

        # ----------------------------------------------------
        # SEATS
        # ----------------------------------------------------

        "available_seats": (
            bus.get("available_seats")
            if bus.get("available_seats") is not None
            else bus.get("availableSeats")
        ),

        "seats": (
            bus.get("available_seats")
            if bus.get("available_seats") is not None
            else bus.get("availableSeats")
        ),

        # ----------------------------------------------------
        # OTHER
        # ----------------------------------------------------

        "ac": bus.get("ac"),

        "sleeper": bus.get("sleeper"),

        "rating": safe_number(
            bus.get("rating")
        ),

        "review_count": (
            bus.get("review_count")
            or bus.get("reviewCount")
        ),

        "amenities": (
            bus.get("amenities")
            or []
        ),

        "boarding_points": (
            bus.get("boarding_points")
            or bus.get("boardingPoints")
            or []
        ),

        "dropping_points": (
            bus.get("dropping_points")
            or bus.get("droppingPoints")
            or []
        ),

        "raw": bus
    }


# ============================================================
# SEARCH BUS
# ============================================================

def search_bus(
    source,
    destination,
    travel_date,
    only_cheapest=False,
    debug=True
):

    if not check_api_key():
        return []

    if not source or not destination:

        print(
            "❌ Source and destination are required."
        )

        return []

    # --------------------------------------------------------
    # NORMALIZE DATE
    # --------------------------------------------------------

    travel_date = normalize_date(
        travel_date
    )

    if not travel_date:

        print(
            f"❌ Invalid travel date: {travel_date}"
        )

        print(
            "Expected format: YYYY-MM-DD"
        )

        return []

    # --------------------------------------------------------
    # SOURCE CITY
    # --------------------------------------------------------

    source_id = get_city_id(
        source
    )

    if source_id is None:

        print(
            f"❌ Could not find source city ID: "
            f"{source}"
        )

        return []

    # --------------------------------------------------------
    # DESTINATION CITY
    # --------------------------------------------------------

    destination_id = get_city_id(
        destination
    )

    if destination_id is None:

        print(
            f"❌ Could not find destination city ID: "
            f"{destination}"
        )

        return []

    # --------------------------------------------------------
    # IMPORTANT PAY2ALL PAYLOAD
    # --------------------------------------------------------
    #
    # Provider expects:
    #
    # doj = YYYY-MM-DD
    #
    # NOT:
    #
    # date
    #
    # --------------------------------------------------------

    payload = {

        "source_id": str(
            source_id
        ),

        "destination_id": str(
            destination_id
        ),

        "doj": travel_date
    }

    print("\n" + "=" * 70)
    print("🚌 BUS SEARCH")
    print("=" * 70)

    print(
        "Source          :",
        source
    )

    print(
        "Destination     :",
        destination
    )

    print(
        "Date            :",
        travel_date
    )

    print(
        "Source ID       :",
        source_id
    )

    print(
        "Destination ID  :",
        destination_id
    )

    print(
        "\nPayload:"
    )

    print(payload)

    # --------------------------------------------------------
    # API REQUEST
    # --------------------------------------------------------

    try:

        response = requests.post(
            BUS_SEARCH_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(
            "\nBus API Status:",
            response.status_code
        )

        # ----------------------------------------------------
        # RAW RESPONSE
        # ----------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            print(
                "\n❌ Invalid JSON:"
            )

            print(
                response.text
            )

            return []

        if debug:

            print(
                "\nRAW BUS RESPONSE:"
            )

            print(data)

        # ----------------------------------------------------
        # HTTP ERROR
        # ----------------------------------------------------

        if response.status_code not in (
            200,
            201
        ):

            print(
                "\n❌ Bus API Error:"
            )

            print(
                response.text
            )

            return []

        # ----------------------------------------------------
        # PAY2ALL STATUS
        # ----------------------------------------------------

        if isinstance(data, dict):

            status_id = data.get(
                "status_id"
            )

            message = data.get(
                "message",
                ""
            )

            if status_id != 1:

                print(
                    "\n❌ Pay2All Error:"
                )

                print(
                    message
                )

                return []

        # ----------------------------------------------------
        # GET TRIPS
        # ----------------------------------------------------

        trips = []

        api_data = data.get(
            "data",
            {}
        )

        if isinstance(api_data, dict):

            trips = api_data.get(
                "trips",
                []
            )

            # Compatibility
            if not trips:

                trips = api_data.get(
                    "results",
                    []
                )

        # ----------------------------------------------------
        # NO BUSES
        # ----------------------------------------------------

        if not trips:

            print(
                "\n⚠️ No buses found."
            )

            print(
                f"🚌 {source} → {destination}"
            )

            print(
                f"📅 Date: {travel_date}"
            )

            return []

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        buses = []

        for trip in trips:

            bus = normalize_bus(
                trip
            )

            if bus:
                buses.append(bus)

        if not buses:

            print(
                "\n❌ Bus data could not be formatted."
            )

            return []

        # ----------------------------------------------------
        # SORT BY FARE
        # ----------------------------------------------------

        buses.sort(
            key=lambda x: (
                x["fare_min"] is None,
                x["fare_min"]
                if x["fare_min"] is not None
                else float("inf")
            )
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        print("\n" + "=" * 70)

        print(
            f"✅ {len(buses)} BUS(ES) FOUND"
        )

        print("=" * 70)

        for i, bus in enumerate(
            buses,
            1
        ):

            print(
                "\n" + "-" * 60
            )

            print(
                f"🚌 BUS {i}"
            )

            print(
                "-" * 60
            )

            print(
                "Operator     :",
                bus["operator"]
            )

            print(
                "Bus Type     :",
                bus["bus_type"]
            )

            print(
                "Departure    :",
                bus["departure"]
            )

            print(
                "Arrival      :",
                bus["arrival"]
            )

            print(
                "Duration     :",
                bus["duration"]
            )

            print(
                "Fare         :",
                bus["fare"]
            )

            print(
                "Seats        :",
                bus["available_seats"]
            )

        # ----------------------------------------------------
        # CHEAPEST ONLY
        # ----------------------------------------------------

        if only_cheapest:

            buses_with_fare = [
                bus
                for bus in buses
                if bus.get("fare_min") is not None
            ]

            if not buses_with_fare:
                return []

            return [
                buses_with_fare[0]
            ]

        return buses

    except requests.exceptions.Timeout:

        print(
            "\n❌ Pay2All request timed out."
        )

        return []

    except requests.exceptions.RequestException as e:

        print(
            "\n❌ Pay2All request error:"
        )

        print(e)

        return []

    except Exception as e:

        print(
            "\n❌ Unexpected bus error:"
        )

        print(e)

        return []


# ============================================================
# CHEAPEST BUS
# ============================================================

def get_cheapest_bus(
    source,
    destination,
    travel_date
):

    buses = search_bus(
        source=source,
        destination=destination,
        travel_date=travel_date,
        only_cheapest=True,
        debug=False
    )

    if not buses:
        return None

    return buses[0]


# ============================================================
# FORMAT FARE
# ============================================================

def format_bus_fare(bus):

    if not bus:
        return "Fare unavailable"

    fare_min = safe_number(
        bus.get("fare_min")
    )

    fare_max = safe_number(
        bus.get("fare_max")
    )

    if fare_min is None:
        return "Fare unavailable"

    if (
        fare_max is not None
        and fare_max != fare_min
    ):

        return (
            f"₹{fare_min:.0f}"
            f" - "
            f"₹{fare_max:.0f}"
        )

    return f"₹{fare_min:.0f}"


# ============================================================
# STREAMLIT FORMAT
# ============================================================

def format_bus(bus):

    if not bus:
        return None

    return {

        "type": "BUS",

        "mode": "Bus",

        # IMPORTANT FOR APP
        "price": bus.get(
            "fare_min"
        ),

        "operator": bus.get(
            "operator",
            "Unknown Operator"
        ),

        "bus_type": bus.get(
            "bus_type",
            "Bus"
        ),

        "departure": bus.get(
            "departure",
            "N/A"
        ),

        "arrival": bus.get(
            "arrival",
            "N/A"
        ),

        "duration": bus.get(
            "duration",
            "N/A"
        ),

        "fare": format_bus_fare(
            bus
        ),

        "fare_min": bus.get(
            "fare_min"
        ),

        "fare_max": bus.get(
            "fare_max"
        ),

        "seats": bus.get(
            "available_seats",
            "N/A"
        ),

        "rating": bus.get(
            "rating"
        ),

        "ac": bus.get(
            "ac"
        ),

        "sleeper": bus.get(
            "sleeper"
        ),

        "amenities": bus.get(
            "amenities",
            []
        ),

        "boarding_points": bus.get(
            "boarding_points",
            []
        ),

        "dropping_points": bus.get(
            "dropping_points",
            []
        ),

        "trip_id": bus.get(
            "trip_id"
        )
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("🚌 PAY2ALL BUS SEARCH TEST")
    print("=" * 70)

    source = input(
        "\nEnter source city: "
    ).strip()

    destination = input(
        "Enter destination city: "
    ).strip()

    travel_date = input(
        "Enter travel date (YYYY-MM-DD): "
    ).strip()

    buses = search_bus(
        source=source,
        destination=destination,
        travel_date=travel_date,
        only_cheapest=False,
        debug=True
    )

    if not buses:

        print("\n" + "=" * 70)

        print(
            f"🚌 No buses available for "
            f"{source} → {destination}"
        )

        print(
            f"📅 Date: {travel_date}"
        )

        print("=" * 70)

    else:

        cheapest = buses[0]

        print("\n" + "=" * 70)
        print("🏆 CHEAPEST BUS")
        print("=" * 70)

        print(
            "Operator     :",
            cheapest["operator"]
        )

        print(
            "Bus Type     :",
            cheapest["bus_type"]
        )

        print(
            "Departure    :",
            cheapest["departure"]
        )

        print(
            "Arrival      :",
            cheapest["arrival"]
        )

        print(
            "Duration     :",
            cheapest["duration"]
        )

        print(
            "Fare         :",
            format_bus_fare(
                cheapest
            )
        )

        print(
            "Seats        :",
            cheapest["available_seats"]
        )

        print(
            "\n📊 Total buses:",
            len(buses)
        )