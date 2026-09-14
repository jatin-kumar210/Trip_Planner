# ============================================================
# TRIPPILOT - PREMIUM AI TRAVEL PLANNER
# ============================================================

import re
from datetime import date

import streamlit as st

from trip_search import search_trip
from ai_planner import create_ai_itinerary

from hotel import (
    search_hotels,
    extract_hotels_from_result,
    remove_duplicates,
    filter_by_budget,
    sort_by_price,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TripPilot",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(135, 35, 75, 0.22),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(104, 30, 64, 0.18),
                transparent 30%
            ),
            #09070a;
        color: #f5e9ee;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #1b0912 0%,
                #0b0709 100%
            );
        border-right:
            1px solid rgba(170, 60, 100, 0.25);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f4dce5;
    }

    section[data-testid="stSidebar"] label {
        color: #cbb2bc !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="input"] {
        background: #160b11 !important;
        border: 1px solid #492033 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #a94a70 !important;
        box-shadow:
            0 0 0 1px rgba(169, 74, 112, 0.25);
    }

    input {
        color: #f6e7ed !important;
    }

    div[data-baseweb="select"] > div {
        background: #160b11 !important;
        border: 1px solid #492033 !important;
        border-radius: 12px !important;
    }

    .stButton > button {
        width: 100%;
        background:
            linear-gradient(
                135deg,
                #a6426b,
                #641d3d
            ) !important;
        color: white !important;
        border:
            1px solid #bd6085 !important;
        border-radius: 13px !important;
        min-height: 46px;
        font-weight: 750 !important;
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 12px 35px rgba(155, 55, 100, 0.35);
    }

    div[data-testid="stImage"] {
        border-radius: 18px;
        overflow: hidden;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                145deg,
                #211018,
                #10090d
            );
        border:
            1px solid #482033 !important;
        border-radius: 20px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #924063 !important;
        box-shadow:
            0 15px 35px rgba(120, 30, 70, 0.15);
    }

    div[data-testid="stMetric"] {
        background: #150a10;
        border:
            1px solid #402031;
        border-radius: 16px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9c838d !important;
    }

    div[data-testid="stMetricValue"] {
        color: #e5a4bb !important;
    }

    button[data-baseweb="tab"] {
        color: #a88d97 !important;
        font-weight: 650 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #e7a5bc !important;
    }

    details {
        background: #12090e !important;
        border: 1px solid #402031 !important;
        border-radius: 14px !important;
    }

    hr {
        border-color: #3b1c2b !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "trip_data" not in st.session_state:
    st.session_state.trip_data = None

if "ai_plan" not in st.session_state:
    st.session_state.ai_plan = None


# ============================================================
# GENERAL HELPERS
# ============================================================

def safe_text(value, default="Not available"):

    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return str(value)

    text = str(value).strip()

    return text if text else default


def get_number(value):

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:

        text = str(value).replace(",", "")

        match = re.search(
            r"\d+(?:\.\d+)?",
            text
        )

        if match:
            return float(match.group())

    except Exception:
        pass

    return None


# ============================================================
# UNIVERSAL LIST NORMALIZER
# IMPORTANT FOR PAY2ALL BUS RESPONSE
# ============================================================

def normalize_list(data):

    if data is None:
        return []

    # Already list
    if isinstance(data, list):
        return data

    # Tuple
    if isinstance(data, tuple):
        return list(data)

    # Dictionary
    if isinstance(data, dict):

        # ----------------------------------------------------
        # DIRECT LIST KEYS
        # ----------------------------------------------------

        for key in [
            "hotels",
            "hotel",
            "items",
            "places",
            "flights",
            "trains",
            "buses",
            "trips",
            "results",
        ]:

            value = data.get(key)

            if isinstance(value, list):
                return value

        # ----------------------------------------------------
        # NESTED DATA
        # Example:
        #
        # {
        #   "data": {
        #       "trips": [...]
        #   }
        # }
        # ----------------------------------------------------

        for key in [
            "data",
            "response",
            "result",
        ]:

            value = data.get(key)

            if isinstance(value, dict):

                nested = normalize_list(value)

                if nested:
                    return nested

        # ----------------------------------------------------
        # SINGLE OBJECT
        # ----------------------------------------------------

        if any(
            key in data
            for key in [
                "name",
                "price",
                "fare",
                "fare_min",
                "fareMin",
                "operator",
                "trip_id",
                "train_name",
                "airline",
            ]
        ):

            return [data]

        return []

    return []


# ============================================================
# DESTINATION IMAGES
# ============================================================

CITY_IMAGES = {

    "goa":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "Goa%20Beach%20-%20Baga%20Beach.jpg?width=1200",

    "mumbai":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "Gateway%20Of%20India.jpg?width=1200",

    "dehradun":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "Dehradun%20city.jpg?width=1200",

    "jaipur":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "Jaipur-Hawa-Mahal.jpg?width=1200",
}


def show_destination_gallery(destination):

    st.subheader(
        "✨ Explore India's Destinations"
    )

    st.caption(
        "A glimpse of places you can explore with TripPilot."
    )

    cities = [
        ("Goa", CITY_IMAGES["goa"]),
        ("Mumbai", CITY_IMAGES["mumbai"]),
        ("Dehradun", CITY_IMAGES["dehradun"]),
        ("Jaipur", CITY_IMAGES["jaipur"]),
    ]

    cols = st.columns(4)

    for index, (city, image) in enumerate(cities):

        with cols[index]:

            try:

                st.image(
                    image,
                    use_container_width=True
                )

            except Exception:

                st.info(
                    f"📍 {city}"
                )

            st.markdown(
                f"**{city}**"
            )

            if city.lower() == destination.lower():

                st.caption(
                    "📍 Your destination"
                )

            else:

                st.caption(
                    "Explore destination"
                )


# ============================================================
# HOTEL HELPERS
# ============================================================

def hotel_price(hotel):

    if not isinstance(hotel, dict):
        return None

    for key in [
        "price",
        "price_per_night",
        "nightly_price",
        "amount",
        "cost",
    ]:

        value = get_number(
            hotel.get(key)
        )

        if value is not None:
            return value

    return None


def extract_hotels_for_app(
    raw_data,
    hotel_budget
):

    extracted_hotels = []

    # --------------------------------------------------------
    # RAW TAVILY RESPONSE
    # --------------------------------------------------------

    if isinstance(raw_data, dict):

        raw_results = raw_data.get(
            "results",
            []
        )

        if isinstance(raw_results, list):

            for result in raw_results:

                if not isinstance(
                    result,
                    dict
                ):
                    continue

                try:

                    hotels = extract_hotels_from_result(
                        result
                    )

                    if hotels:

                        extracted_hotels.extend(
                            hotels
                        )

                except Exception:
                    continue

    # --------------------------------------------------------
    # ALREADY CLEAN HOTEL LIST
    # --------------------------------------------------------

    elif isinstance(raw_data, list):

        for hotel in raw_data:

            if not isinstance(
                hotel,
                dict
            ):
                continue

            if hotel.get("name"):

                extracted_hotels.append(
                    hotel
                )

    if not extracted_hotels:
        return []

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    try:

        extracted_hotels = remove_duplicates(
            extracted_hotels
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # BUDGET FILTER
    # --------------------------------------------------------

    try:

        extracted_hotels = filter_by_budget(
            extracted_hotels,
            hotel_budget
        )

    except Exception:

        extracted_hotels = [
            hotel
            for hotel in extracted_hotels
            if (
                hotel_price(hotel) is not None
                and hotel_price(hotel) <= hotel_budget
            )
        ]

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    try:

        extracted_hotels = sort_by_price(
            extracted_hotels
        )

    except Exception:

        extracted_hotels.sort(
            key=lambda hotel: (
                hotel_price(hotel) is None,
                hotel_price(hotel)
                if hotel_price(hotel) is not None
                else 999999
            )
        )

    return extracted_hotels


def get_hotels_safely(
    destination,
    hotel_budget,
    existing_hotels
):

    hotels = extract_hotels_for_app(
        existing_hotels,
        hotel_budget
    )

    if hotels:
        return hotels

    try:

        fallback = search_hotels(
            destination,
            hotel_budget
        )

        hotels = extract_hotels_for_app(
            fallback,
            hotel_budget
        )

        return hotels

    except Exception as e:

        st.warning(
            f"Hotel search unavailable: {e}"
        )

        return []


def choose_best_hotel(hotels):

    hotels = normalize_list(
        hotels
    )

    priced = []

    for hotel in hotels:

        if not isinstance(
            hotel,
            dict
        ):
            continue

        price = hotel_price(
            hotel
        )

        if price is not None:

            priced.append(
                (
                    price,
                    hotel
                )
            )

    if priced:

        priced.sort(
            key=lambda x: x[0]
        )

        return priced[0][1]

    if hotels:
        return hotels[0]

    return None


# ============================================================
# HOTEL UI
# ============================================================

def show_hotel(hotel):

    st.markdown(
        "### 🏨 Recommended Stay"
    )

    if not hotel:

        st.warning(
            "🏨 No hotel within your budget was found."
        )

        st.caption(
            "Try increasing your hotel budget."
        )

        return

    name = safe_text(
        hotel.get("name"),
        "Hotel"
    )

    location = safe_text(
        hotel.get("location")
    )

    price = hotel_price(
        hotel
    )

    rating_value = hotel.get(
        "rating"
    )

    if rating_value is not None:

        rating_number = get_number(
            rating_value
        )

        if rating_number is not None:
            rating = f"{rating_number:.1f}"
        else:
            rating = safe_text(
                rating_value
            )

    else:

        rating = "Not available"

    taxes_value = hotel.get(
        "taxes"
    )

    if taxes_value is not None:

        taxes_number = get_number(
            taxes_value
        )

        if taxes_number is not None:

            taxes = (
                f"₹{taxes_number:,.0f}"
            )

        else:

            taxes = safe_text(
                taxes_value
            )

    else:

        taxes = "Not available"

    source = safe_text(
        hotel.get("source")
    )

    url = hotel.get(
        "url"
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"## 🏨 {name}"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            if price is not None:

                st.metric(
                    "Price / Night",
                    f"₹{price:,.0f}"
                )

            else:

                st.metric(
                    "Price / Night",
                    "N/A"
                )

        with c2:

            st.metric(
                "⭐ Rating",
                rating
            )

        with c3:

            st.metric(
                "🧾 Taxes",
                taxes
            )

        st.write(
            f"📍 **Location:** {location}"
        )

        if source != "Not available":

            st.caption(
                f"Source: {source}"
            )

        if url:

            st.link_button(
                "🔗 View Hotel",
                url,
                use_container_width=True
            )


# ============================================================
# TRANSPORT PRICE
# ============================================================

def transport_price(item):

    if not isinstance(
        item,
        dict
    ):
        return None

    # --------------------------------------------------------
    # NORMAL PAY2ALL FIELDS
    # --------------------------------------------------------

    for key in [
        "fare_min",
        "fareMin",
        "price",
        "amount",
        "fare",
        "cost",
        "price_min",
        "min_fare",
        "minimum_fare",
    ]:

        value = get_number(
            item.get(key)
        )

        if value is not None:
            return value

    # --------------------------------------------------------
    # NESTED FARE OBJECT
    # --------------------------------------------------------

    fare_data = item.get(
        "fare"
    )

    if isinstance(
        fare_data,
        dict
    ):

        for key in [
            "min",
            "minimum",
            "fare_min",
            "fareMin",
            "price",
            "amount",
        ]:

            value = get_number(
                fare_data.get(key)
            )

            if value is not None:
                return value

    return None


# ============================================================
# FIND CHEAPEST TRANSPORT
# ============================================================

def find_cheapest_transport(
    transport
):

    if not isinstance(
        transport,
        dict
    ):
        return None

    candidates = []

    # ========================================================
    # FLIGHTS
    # ========================================================

    flights = normalize_list(
        transport.get("flights")
    )

    for flight in flights:

        if not isinstance(
            flight,
            dict
        ):
            continue

        price = transport_price(
            flight
        )

        if price is not None:

            candidates.append(
                {
                    "mode": "✈️ Flight",
                    "price": price,
                    "data": flight
                }
            )

    # ========================================================
    # TRAINS
    # ========================================================

    trains = normalize_list(
        transport.get("trains")
    )

    for train in trains:

        if not isinstance(
            train,
            dict
        ):
            continue

        price = transport_price(
            train
        )

        if price is not None:

            candidates.append(
                {
                    "mode": "🚆 Train",
                    "price": price,
                    "data": train
                }
            )

    # ========================================================
    # BUSES
    # ========================================================

    buses_raw = transport.get(
        "buses"
    )

    buses = normalize_list(
        buses_raw
    )

    # --------------------------------------------------------
    # EXTRA SAFETY:
    #
    # If buses is still empty, try nested structures manually.
    # --------------------------------------------------------

    if not buses and isinstance(
        buses_raw,
        dict
    ):

        buses_data = buses_raw.get(
            "data"
        )

        if isinstance(
            buses_data,
            dict
        ):

            buses = normalize_list(
                buses_data
            )

    for bus in buses:

        if not isinstance(
            bus,
            dict
        ):
            continue

        price = transport_price(
            bus
        )

        if price is not None:

            candidates.append(
                {
                    "mode": "🚌 Bus",
                    "price": price,
                    "data": bus
                }
            )

    # ========================================================
    # NOTHING FOUND
    # ========================================================

    if not candidates:
        return None

    # ========================================================
    # CHEAPEST FIRST
    # ========================================================

    candidates.sort(
        key=lambda x: x["price"]
    )

    return candidates[0]


# ============================================================
# TRANSPORT DETAILS
# ============================================================

def transport_details(
    option
):

    if not option:
        return []

    data = option.get(
        "data",
        {}
    )

    if not isinstance(
        data,
        dict
    ):
        return []

    details = []

    # --------------------------------------------------------
    # OPERATOR
    # --------------------------------------------------------

    operator = (
        data.get("operator")
        or data.get("airline")
        or data.get("train_name")
        or data.get("name")
    )

    if isinstance(
        operator,
        dict
    ):

        operator = (
            operator.get("name")
            or operator.get("airline")
        )

    if operator:

        details.append(
            f"🏢 {safe_text(operator)}"
        )

    # --------------------------------------------------------
    # BUS TYPE
    # --------------------------------------------------------

    bus_type = (
        data.get("bus_type")
        or data.get("busType")
        or data.get("type")
    )

    if bus_type:

        details.append(
            f"🚍 {safe_text(bus_type)}"
        )

    # --------------------------------------------------------
    # DEPARTURE
    # --------------------------------------------------------

    departure = (
        data.get("departure")
        or data.get("departure_time")
        or data.get("departureTime")
    )

    if departure:

        details.append(
            f"🕐 Departure: {safe_text(departure)}"
        )

    # --------------------------------------------------------
    # ARRIVAL
    # --------------------------------------------------------

    arrival = (
        data.get("arrival")
        or data.get("arrival_time")
        or data.get("arrivalTime")
    )

    if arrival:

        details.append(
            f"🏁 Arrival: {safe_text(arrival)}"
        )

    # --------------------------------------------------------
    # DURATION
    # --------------------------------------------------------

    duration = (
        data.get("duration")
        or data.get("duration_min")
        or data.get("durationMin")
    )

    if duration:

        st_duration = safe_text(
            duration
        )

        details.append(
            f"⏱️ Duration: {st_duration}"
        )

    # --------------------------------------------------------
    # SEATS
    # --------------------------------------------------------

    seats = (
        data.get("available_seats")
        or data.get("seatsAvailable")
        or data.get("seats")
    )

    if seats is not None:

        details.append(
            f"💺 {safe_text(seats)} seats available"
        )

    # --------------------------------------------------------
    # MAX FARE
    # --------------------------------------------------------

    max_fare = (
        data.get("fare_max")
        or data.get("fareMax")
        or data.get("price_max")
    )

    if max_fare is not None:

        max_fare_number = get_number(
            max_fare
        )

        if max_fare_number is not None:

            details.append(
                f"💰 Fare up to ₹{max_fare_number:,.0f}"
            )

    return details


# ============================================================
# CHEAPEST TRANSPORT UI
# ============================================================

def show_cheapest_transport(
    cheapest
):

    st.markdown(
        "### 🏆 Cheapest Way To Travel"
    )

    if not cheapest:

        st.warning(
            "No transport with price information was found."
        )

        return

    details = transport_details(
        cheapest
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"# {cheapest['mode']}"
        )

        st.markdown(
            f"## ₹{cheapest['price']:,.0f}"
        )

        st.caption(
            "TripPilot selected the lowest available "
            "transport price."
        )

        for detail in details:

            st.write(
                detail
            )


# ============================================================
# PLACES
# ============================================================

def display_places(
    places
):

    places = normalize_list(
        places
    )

    if not places:

        st.info(
            "No places were found."
        )

        return

    places = places[:12]

    for start in range(
        0,
        len(places),
        3
    ):

        row = places[
            start:start + 3
        ]

        cols = st.columns(3)

        for i, place in enumerate(row):

            if not isinstance(
                place,
                dict
            ):
                continue

            name = safe_text(
                place.get("name"),
                "Attraction"
            )

            place_type = safe_text(
                place.get("type"),
                "Attraction"
            )

            description = safe_text(
                place.get("description"),
                "Explore this destination."
            )

            url = place.get(
                "url"
            )

            with cols[i]:

                with st.container(
                    border=True
                ):

                    st.caption(
                        f"DESTINATION {start + i + 1}"
                    )

                    st.subheader(
                        f"📍 {name}"
                    )

                    st.caption(
                        f"🎯 {place_type}"
                    )

                    st.write(
                        description[:280]
                    )

                    if url:

                        st.link_button(
                            "🔗 Explore Place",
                            url,
                            use_container_width=True
                        )


# ============================================================
# AI HELPERS
# ============================================================

def hotel_for_ai(
    hotel
):

    if not hotel:

        return "No hotel available."

    return f"""
Hotel name:
{safe_text(hotel.get("name"))}

Location:
{safe_text(hotel.get("location"))}

Price per night:
₹{safe_text(hotel.get("price"))}

Rating:
{safe_text(hotel.get("rating"))}

Taxes:
{safe_text(hotel.get("taxes"))}
"""


def transport_for_ai(
    option
):

    if not option:

        return "No transport available."

    data = option.get(
        "data",
        {}
    )

    details = transport_details(
        option
    )

    return (
        f"CHEAPEST TRANSPORT:\n"
        f"{option['mode']}\n"
        f"PRICE: ₹{option['price']:.0f}\n"
        + "\n".join(details)
        + "\n"
        + f"Raw transport data: {data}"
    )


def places_for_ai(
    places
):

    places = normalize_list(
        places
    )

    result = []

    for i, place in enumerate(
        places[:20],
        1
    ):

        if not isinstance(
            place,
            dict
        ):
            continue

        result.append(
            f"{i}. "
            f"{safe_text(place.get('name'))} - "
            f"{safe_text(place.get('description'))[:300]}"
        )

    return "\n".join(
        result
    )


# ============================================================
# ITINERARY DISPLAY
# ============================================================

def show_itinerary(
    plan
):

    if not plan:

        st.info(
            "Generate your AI itinerary."
        )

        return

    pattern = re.compile(
        r"(?i)(DAY\s+\d+)"
    )

    matches = list(
        pattern.finditer(
            plan
        )
    )

    if not matches:

        st.markdown(
            plan
        )

        return

    for index, match in enumerate(
        matches
    ):

        day_title = match.group(
            1
        )

        start = match.end()

        if index + 1 < len(matches):

            end = matches[
                index + 1
            ].start()

        else:

            end = len(plan)

        content = plan[
            start:end
        ].strip()

        st.markdown(
            f"## 🗓️ {day_title}"
        )

        with st.container(
            border=True
        ):

            lines = content.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                lower = line.lower()

                if (
                    lower.startswith("morning")
                    or lower.startswith("afternoon")
                    or lower.startswith("evening")
                    or lower.startswith("night")
                    or lower.startswith("breakfast")
                    or lower.startswith("lunch")
                    or lower.startswith("dinner")
                ):

                    st.markdown(
                        f"### {line}"
                    )

                elif line.startswith(
                    ("-", "•", "*")
                ):

                    st.markdown(
                        f"• {line.lstrip('-•* ').strip()}"
                    )

                else:

                    st.write(
                        line
                    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🧭 TripPilot"
    )

    st.caption(
        "AI-powered travel planner"
    )

    st.divider()

    source = st.text_input(
        "📍 Starting city",
        value="Dehradun"
    )

    destination = st.text_input(
        "🌎 Destination",
        value="Goa"
    )

    travel_date = st.date_input(
        "📅 Travel date",
        value=date.today()
    )

    days = st.number_input(
        "🗓️ Number of days",
        min_value=1,
        max_value=30,
        value=5
    )

    budget = st.number_input(
        "💰 Total trip budget (₹)",
        min_value=1000,
        max_value=1000000,
        value=12000,
        step=500
    )

    hotel_budget = st.number_input(
        "🏨 Hotel budget / night (₹)",
        min_value=300,
        max_value=100000,
        value=1500,
        step=100
    )

    interests = st.text_input(
        "🎯 Interests",
        value="beaches, adventure, sightseeing"
    )

    st.write("")

    plan_trip = st.button(
        "🚀 PLAN MY JOURNEY",
        use_container_width=True
    )


# ============================================================
# PLAN TRIP
# ============================================================

if plan_trip:

    st.session_state.trip_data = None
    st.session_state.ai_plan = None

    with st.spinner(
        "🧭 Searching flights, trains, buses, hotels and places..."
    ):

        try:

            trip_data = search_trip(
                origin=source,
                destination=destination,
                travel_date=str(
                    travel_date
                ),
                hotel_budget=hotel_budget,
                interests=interests
            )

            if not isinstance(
                trip_data,
                dict
            ):

                raise ValueError(
                    "search_trip() did not return a dictionary."
                )

            st.session_state.trip_data = trip_data

        except Exception as e:

            st.error(
                f"❌ Trip search failed:\n\n{e}"
            )

            st.stop()


# ============================================================
# HOME
# ============================================================

if not st.session_state.trip_data:

    st.markdown(
        """
        # 🧭 TripPilot

        ### Your AI-powered travel companion

        Plan smarter.  
        Travel better.  
        Explore more.
        """
    )

    st.write(
        "TripPilot searches transport, hotels and attractions, "
        "then uses AI to create your complete journey."
    )

    st.divider()

    show_destination_gallery(
        destination
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "✈️ Transport",
            "Compare"
        )

    with c2:

        st.metric(
            "🏨 Hotels",
            "Budget"
        )

    with c3:

        st.metric(
            "🤖 AI Plan",
            "Day-by-Day"
        )

    st.info(
        "👈 Enter your trip details and click "
        "**PLAN MY JOURNEY**."
    )


# ============================================================
# RESULTS
# ============================================================

trip_data = st.session_state.trip_data

if trip_data:

    transport = trip_data.get(
        "transport",
        {}
    )

    # ========================================================
    # HOTELS
    # ========================================================

    raw_hotels = trip_data.get(
        "hotels",
        []
    )

    hotels = get_hotels_safely(
        destination=destination,
        hotel_budget=hotel_budget,
        existing_hotels=raw_hotels
    )

    best_hotel = choose_best_hotel(
        hotels
    )

    # ========================================================
    # PLACES
    # ========================================================

    places = normalize_list(
        trip_data.get(
            "places",
            []
        )
    )

    # ========================================================
    # CHEAPEST TRANSPORT
    # ========================================================

    cheapest = find_cheapest_transport(
        transport
    )

    # ========================================================
    # COST
    # ========================================================

    travel_cost = 0

    if cheapest:

        travel_cost = cheapest[
            "price"
        ]

    hotel_nightly = (
        hotel_price(
            best_hotel
        )
        if best_hotel
        else 0
    )

    hotel_total = (
        hotel_nightly * days
        if hotel_nightly
        else 0
    )

    basic_cost = (
        travel_cost
        + hotel_total
    )

    remaining = (
        budget
        - basic_cost
    )

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        f"""
        # 🧭 {source} → {destination}

        **📅 {travel_date}**
        &nbsp;&nbsp;•&nbsp;&nbsp;
        **🗓️ {days} Days**
        &nbsp;&nbsp;•&nbsp;&nbsp;
        **💰 ₹{budget:,.0f} Budget**
        """
    )

    show_destination_gallery(
        destination
    )

    st.divider()

    # ========================================================
    # METRICS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🏆 Cheapest Travel",
            (
                f"₹{travel_cost:,.0f}"
                if travel_cost
                else "N/A"
            )
        )

    with c2:

        st.metric(
            "🏨 Hotel / Night",
            (
                f"₹{hotel_nightly:,.0f}"
                if hotel_nightly
                else "N/A"
            )
        )

    with c3:

        st.metric(
            "📍 Places",
            len(places)
        )

    with c4:

        st.metric(
            "💰 Remaining",
            f"₹{remaining:,.0f}"
        )

    st.write("")

    (
        tab_overview,
        tab_places,
        tab_ai,
        tab_data
    ) = st.tabs(
        [
            "🧭 Overview",
            "📍 Explore",
            "🤖 AI Journey",
            "🔎 Data"
        ]
    )

    # ========================================================
    # OVERVIEW
    # ========================================================

    with tab_overview:

        show_cheapest_transport(
            cheapest
        )

        st.divider()

        show_hotel(
            best_hotel
        )

        st.divider()

        st.subheader(
            "💰 Budget Breakdown"
        )

        b1, b2, b3 = st.columns(3)

        with b1:

            st.metric(
                "🚌/🚆/✈️ Transport",
                f"₹{travel_cost:,.0f}"
            )

        with b2:

            st.metric(
                f"🏨 Hotel × {days}",
                f"₹{hotel_total:,.0f}"
            )

        with b3:

            st.metric(
                "📊 Basic Cost",
                f"₹{basic_cost:,.0f}"
            )

        if remaining >= 0:

            st.success(
                f"✅ Approximately ₹{remaining:,.0f} "
                "is left for food, local transport "
                "and activities."
            )

        else:

            st.error(
                f"⚠️ Transport + hotel exceeds your "
                f"budget by ₹{abs(remaining):,.0f}."
            )

    # ========================================================
    # PLACES
    # ========================================================

    with tab_places:

        st.title(
            f"📍 Places to Explore in {destination}"
        )

        st.caption(
            f"Based on your interests: {interests}"
        )

        display_places(
            places
        )

    # ========================================================
    # AI JOURNEY
    # ========================================================

    with tab_ai:

        st.title(
            "🤖 Your AI Travel Journey"
        )

        st.write(
            "Generate a complete Day 1 → Day N itinerary."
        )

        st.info(
            "Gemini will use your destination, places, "
            "hotel and cheapest transport information."
        )

        if st.button(
            "✨ GENERATE MY DAY-BY-DAY JOURNEY",
            key="generate_ai"
        ):

            with st.spinner(
                "🤖 Gemini is creating your journey..."
            ):

                try:

                    plan = create_ai_itinerary(
                        source=source,
                        destination=destination,
                        travel_date=str(
                            travel_date
                        ),
                        days=days,
                        budget=budget,
                        interests=interests,
                        places=places_for_ai(
                            places
                        ),
                        hotel=hotel_for_ai(
                            best_hotel
                        ),
                        transport=transport_for_ai(
                            cheapest
                        )
                    )

                    st.session_state.ai_plan = plan

                except Exception as e:

                    st.error(
                        f"❌ AI itinerary error:\n\n{e}"
                    )

        if st.session_state.ai_plan:

            st.success(
                "✨ Your complete journey is ready!"
            )

            show_itinerary(
                st.session_state.ai_plan
            )

        else:

            st.info(
                "Click the button above to generate "
                "your itinerary."
            )

    # ========================================================
    # DATA
    # ========================================================

    with tab_data:

        st.subheader(
            "🔎 TripPilot Data"
        )

        # ----------------------------------------------------
        # CHEAPEST TRANSPORT
        # ----------------------------------------------------

        with st.expander(
            "🏆 Cheapest Transport"
        ):

            if cheapest:

                st.write(
                    f"Mode: **{cheapest['mode']}**"
                )

                st.write(
                    f"Minimum Fare: **₹{cheapest['price']:,.0f}**"
                )

                st.json(
                    cheapest
                )

            else:

                st.warning(
                    "No cheapest transport detected."
                )

        # ----------------------------------------------------
        # RAW TRANSPORT
        # ----------------------------------------------------

        with st.expander(
            "🚍 Raw Transport Data"
        ):

            st.json(
                transport
            )

        # ----------------------------------------------------
        # HOTELS
        # ----------------------------------------------------

        with st.expander(
            "🏨 Hotels"
        ):

            st.write(
                f"Hotels found: {len(hotels)}"
            )

            st.json(
                hotels
            )

        # ----------------------------------------------------
        # PLACES
        # ----------------------------------------------------

        with st.expander(
            "📍 Places"
        ):

            st.write(
                f"Places found: {len(places)}"
            )

            st.json(
                places
            )

        # ----------------------------------------------------
        # COMPLETE DATA
        # ----------------------------------------------------

        with st.expander(
            "🔎 Complete Trip Data"
        ):

            st.json(
                trip_data
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧭 TripPilot • AI Travel Planner • "
    "Transport + Hotels + Places + Gemini AI"
)