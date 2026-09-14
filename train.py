import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# RAILRADAR CONFIG
# =========================================================

RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY")

RAILRADAR_BASE_URL = "https://api.railradar.in/v1"


# =========================================================
# STATION CODES
# =========================================================

STATION_CODES = {
    "dehradun": "DDN",
    "ddn": "DDN",

    "haridwar": "HW",
    "hw": "HW",

    "rishikesh": "RKSH",
    "rksh": "RKSH",

    # Delhi
    "delhi": "NDLS",
    "new delhi": "NDLS",
    "ndls": "NDLS",

    "old delhi": "DLI",
    "dli": "DLI",

    "delhi cantt": "DEC",
    "dec": "DEC",

    "lucknow": "LKO",
    "lko": "LKO",

    "kanpur": "CNB",
    "cnb": "CNB",

    "agra": "AGC",
    "agra cantt": "AGC",
    "agc": "AGC",

    "varanasi": "BSB",
    "bsb": "BSB",

    "jaipur": "JP",
    "jp": "JP",

    "jodhpur": "JU",
    "ju": "JU",

    "udaipur": "UDZ",
    "udz": "UDZ",

    "amritsar": "ASR",
    "asr": "ASR",

    "ludhiana": "LDH",
    "ldh": "LDH",

    # NOTE:
    # Chandigarh railway station code is CDG,
    # but CDG can be confused with airport codes.
    "chandigarh": "CDG",
    "cdg": "CDG",

    "mumbai": "MMCT",
    "mumbai central": "MMCT",
    "mmct": "MMCT",

    "csmt": "CSMT",

    "pune": "PUNE",

    "ahmedabad": "ADI",
    "adi": "ADI",

    "bhopal": "BPL",
    "bpl": "BPL",

    "indore": "INDB",
    "indb": "INDB",

    "patna": "PNBE",
    "pnbe": "PNBE",

    "kolkata": "KOAA",
    "koaa": "KOAA",

    "howrah": "HWH",
    "hwh": "HWH",

    "goa": "MAO",
    "madgaon": "MAO",
    "mao": "MAO",
}


# =========================================================
# MULTIPLE STATIONS FOR CITIES
# =========================================================

CITY_STATIONS = {
    "delhi": ["NDLS", "DLI", "DEC"],
    "new delhi": ["NDLS", "DLI", "DEC"],
}


# =========================================================
# GET STATION CODE
# =========================================================

def get_station_code(city):
    """
    Convert city/station name to the primary railway station code.
    """

    if not city:
        return None

    city = str(city).strip().lower()

    return STATION_CODES.get(city)


# =========================================================
# GET ALL STATIONS FOR A CITY
# =========================================================

def get_station_codes(city):
    """
    Return all useful station codes for a city.

    Example:
        Delhi -> ['NDLS', 'DLI', 'DEC']
        Dehradun -> ['DDN']
    """

    if not city:
        return []

    city = str(city).strip().lower()

    # Special multi-station cities
    if city in CITY_STATIONS:
        return CITY_STATIONS[city]

    # Normal city
    code = STATION_CODES.get(city)

    if code:
        return [code]

    # If user directly gives station code
    if len(city) <= 5 and city.upper() in STATION_CODES.values():
        return [city.upper()]

    return []


# =========================================================
# NORMALIZE DATE
# =========================================================

def normalize_date(travel_date):
    """
    Convert common date formats into YYYY-MM-DD.
    """

    if not travel_date:
        raise ValueError("Travel date is required.")

    travel_date = str(travel_date).strip()

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            date_obj = datetime.strptime(travel_date, fmt)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date: {travel_date}\n"
        "Expected format: YYYY-MM-DD\n"
        "Example: 2026-09-27"
    )


# =========================================================
# SEARCH ONE ROUTE
# =========================================================

def _search_single_route(from_station, to_station, travel_date):

    url = (
        f"{RAILRADAR_BASE_URL}"
        f"/trains/between/"
        f"{from_station}/{to_station}"
    )

    params = {
        "date": travel_date
    }

    headers = {
        "Authorization": f"Bearer {RAILRADAR_API_KEY}",
        "Accept": "application/json"
    }

    print("\n" + "-" * 70)
    print(f"🔎 Route: {from_station} → {to_station}")
    print(f"📅 Date : {travel_date}")
    print("-" * 70)

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

    except requests.exceptions.Timeout:

        print("❌ Request timed out.")
        return []

    except requests.exceptions.ConnectionError:

        print("❌ Could not connect to RailRadar.")
        return []

    except requests.exceptions.RequestException as e:

        print(f"❌ Request error: {e}")
        return []

    print(f"API Status: {response.status_code}")

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    if response.status_code == 200:

        try:
            result = response.json()

        except ValueError:

            print("❌ RailRadar returned invalid JSON.")
            print(response.text)
            return []

        # Debug response
        # Uncomment if needed:
        # print("RAW RESPONSE:")
        # print(result)

        if result.get("success") is False:

            print("❌ RailRadar API returned an error.")

            error = result.get("error")

            if error:
                print(error)

            return []

        data = result.get("data", {})

        if not isinstance(data, dict):

            print("❌ Unexpected response format.")
            return []

        trains = data.get("trains", [])

        if not trains:

            print(f"ℹ️ No trains: {from_station} → {to_station}")

            return []

        print(f"✅ Found {len(trains)} train(s).")

        return trains

    # -----------------------------------------------------
    # 401
    # -----------------------------------------------------

    elif response.status_code == 401:

        print("❌ Unauthorized.")
        print(
            "Your RailRadar API key is missing, "
            "invalid, or expired."
        )

        return []

    # -----------------------------------------------------
    # 404
    # -----------------------------------------------------

    elif response.status_code == 404:

        print("❌ Route/station not found.")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

        return []

    # -----------------------------------------------------
    # 429
    # -----------------------------------------------------

    elif response.status_code == 429:

        print("❌ API rate limit exceeded.")

        return []

    # -----------------------------------------------------
    # 400
    # -----------------------------------------------------

    elif response.status_code == 400:

        print("❌ Bad request.")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

        return []

    # -----------------------------------------------------
    # OTHER ERRORS
    # -----------------------------------------------------

    else:

        print("❌ RailRadar API Error.")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

        return []


# =========================================================
# REMOVE DUPLICATE TRAINS
# =========================================================

def remove_duplicate_trains(trains):
    """
    Remove duplicate trains using train number.
    """

    unique = {}
    no_number = []

    for item in trains:

        train = item.get("train", {})

        train_number = train.get("number")

        if train_number:

            unique[str(train_number)] = item

        else:

            no_number.append(item)

    return list(unique.values()) + no_number


# =========================================================
# SEARCH TRAINS
# =========================================================

def search_trains(from_station, to_station, travel_date):

    if not RAILRADAR_API_KEY:

        print("\n❌ RAILRADAR_API_KEY not found.")

        print("\nCreate a .env file in your TripPilot folder:")

        print("""
RAILRADAR_API_KEY=your_actual_api_key
""")

        return []

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    try:

        travel_date = normalize_date(travel_date)

    except ValueError as e:

        print(f"\n❌ {e}")

        return []

    # -----------------------------------------------------
    # STATION INPUT
    # -----------------------------------------------------

    from_station = str(from_station).strip().upper()
    to_station = str(to_station).strip().upper()

    print("\n" + "=" * 75)
    print("🚆 TripPilot - RailRadar Train Search")
    print("=" * 75)

    print(f"📍 From : {from_station}")
    print(f"📍 To   : {to_station}")
    print(f"📅 Date : {travel_date}")

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    trains = _search_single_route(
        from_station,
        to_station,
        travel_date
    )

    # -----------------------------------------------------
    # IF FOUND
    # -----------------------------------------------------

    if trains:

        trains = remove_duplicate_trains(trains)

        print("\n" + "=" * 75)
        print(f"✅ Total unique trains found: {len(trains)}")
        print("=" * 75)

        return trains

    # -----------------------------------------------------
    # NOTHING FOUND
    # -----------------------------------------------------

    print("\n❌ No trains found for this route/date.")

    return []


# =========================================================
# SEARCH TRAINS BY CITY
# =========================================================

def search_trains_by_city(
    from_city,
    to_city,
    travel_date
):
    """
    Smart city-level train search.

    Delhi automatically searches:
        NDLS
        DLI
        DEC
    """

    if not RAILRADAR_API_KEY:

        print("\n❌ RAILRADAR_API_KEY not found.")

        return []

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    try:

        travel_date = normalize_date(travel_date)

    except ValueError as e:

        print(f"\n❌ {e}")

        return []

    # -----------------------------------------------------
    # GET STATIONS
    # -----------------------------------------------------

    from_stations = get_station_codes(from_city)
    to_stations = get_station_codes(to_city)

    if not from_stations:

        print(
            f"\n❌ No railway station found for "
            f"'{from_city}'."
        )

        return []

    if not to_stations:

        print(
            f"\n❌ No railway station found for "
            f"'{to_city}'."
        )

        return []

    print("\n" + "=" * 75)
    print("🚆 TripPilot - Smart Train Search")
    print("=" * 75)

    print(f"📍 From city : {from_city}")
    print(f"🚉 Stations  : {', '.join(from_stations)}")

    print(f"📍 To city   : {to_city}")
    print(f"🚉 Stations  : {', '.join(to_stations)}")

    print(f"📅 Date      : {travel_date}")

    print("=" * 75)

    all_trains = []

    # -----------------------------------------------------
    # SEARCH EVERY STATION COMBINATION
    # -----------------------------------------------------

    for from_station in from_stations:

        for to_station in to_stations:

            # Same station shouldn't be searched
            if from_station == to_station:
                continue

            trains = _search_single_route(
                from_station,
                to_station,
                travel_date
            )

            if trains:

                # Store station information
                for item in trains:

                    item["_search_from"] = from_station
                    item["_search_to"] = to_station

                all_trains.extend(trains)

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    all_trains = remove_duplicate_trains(all_trains)

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    print("\n" + "=" * 75)

    if all_trains:

        print(
            f"✅ Total unique trains found: "
            f"{len(all_trains)}"
        )

    else:

        print(
            f"❌ No trains found for "
            f"{from_city} → {to_city}"
        )

    print("=" * 75)

    return all_trains


# =========================================================
# DISPLAY TRAINS
# =========================================================

def display_trains(trains):

    if not trains:

        return

    print("\n")
    print("=" * 80)
    print("🚆 TRAIN RESULTS")
    print("=" * 80)

    for index, item in enumerate(trains, start=1):

        train = item.get("train", {})

        from_data = item.get("from", {})

        to_data = item.get("to", {})

        # -------------------------------------------------
        # TRAIN DETAILS
        # -------------------------------------------------

        train_number = train.get(
            "number",
            "N/A"
        )

        train_name = train.get(
            "name",
            "Unknown Train"
        )

        train_type = train.get(
            "type",
            "N/A"
        )

        run_days = train.get(
            "runDays",
            []
        )

        # -------------------------------------------------
        # TIMINGS
        # -------------------------------------------------

        departure = from_data.get(
            "departure",
            "N/A"
        )

        arrival = to_data.get(
            "arrival",
            "N/A"
        )

        # -------------------------------------------------
        # DURATION
        # -------------------------------------------------

        duration_minutes = item.get(
            "duration"
        )

        if duration_minutes is not None:

            try:

                duration_minutes = int(
                    duration_minutes
                )

                hours = duration_minutes // 60
                minutes = duration_minutes % 60

                if hours > 0:

                    duration = (
                        f"{hours}h {minutes}m"
                    )

                else:

                    duration = f"{minutes}m"

            except (ValueError, TypeError):

                duration = "N/A"

        else:

            duration = "N/A"

        # -------------------------------------------------
        # DISTANCE
        # -------------------------------------------------

        distance = item.get(
            "distance"
        )

        if distance is not None:

            distance_text = (
                f"{distance} km"
            )

        else:

            distance_text = "N/A"

        # -------------------------------------------------
        # RUNNING DAYS
        # -------------------------------------------------

        if run_days:

            running_days = ", ".join(
                str(day).upper()
                for day in run_days
            )

        else:

            running_days = "N/A"

        # -------------------------------------------------
        # SEARCH STATIONS
        # -------------------------------------------------

        search_from = item.get(
            "_search_from",
            ""
        )

        search_to = item.get(
            "_search_to",
            ""
        )

        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        print(
            f"\n{index}. {train_name}"
        )

        print(
            f"   Train No    : {train_number}"
        )

        print(
            f"   Type        : {train_type}"
        )

        if search_from and search_to:

            print(
                f"   Route       : "
                f"{search_from} → {search_to}"
            )

        print(
            f"   Departure   : {departure}"
        )

        print(
            f"   Arrival     : {arrival}"
        )

        print(
            f"   Duration    : {duration}"
        )

        print(
            f"   Distance    : {distance_text}"
        )

        print(
            f"   Runs        : {running_days}"
        )

        print("-" * 80)

    print(
        f"\nTotal trains found: {len(trains)}"
    )

    print("=" * 80)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 75)
    print("🚆 TripPilot - Train Search")
    print("=" * 75)

    # -----------------------------------------------------
    # USER INPUT
    # -----------------------------------------------------

    from_city = input(
        "\nFrom city: "
    ).strip()

    to_city = input(
        "To city: "
    ).strip()

    travel_date = input(
        "Travel date (YYYY-MM-DD): "
    ).strip()

    # -----------------------------------------------------
    # VALIDATE CITIES
    # -----------------------------------------------------

    from_stations = get_station_codes(
        from_city
    )

    to_stations = get_station_codes(
        to_city
    )

    if not from_stations:

        print(
            f"\n❌ Station code not found "
            f"for '{from_city}'."
        )

        print(
            "\nAdd this city/station to "
            "STATION_CODES."
        )

        exit()

    if not to_stations:

        print(
            f"\n❌ Station code not found "
            f"for '{to_city}'."
        )

        print(
            "\nAdd this city/station to "
            "STATION_CODES."
        )

        exit()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    trains = search_trains_by_city(
        from_city,
        to_city,
        travel_date
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    display_trains(trains)