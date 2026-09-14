# ============================================================
# TRIPPILOT - TRANSPORT COMPARISON
# ============================================================

def compare_transport(
    bus_results,
    train_results,
    flight_results
):

    options = []

    # BUS
    for bus in bus_results:

        price = bus.get("price")

        if isinstance(price, (int, float)):

            options.append({
                "type": "🚌 BUS",
                "price": price,
                "details": bus
            })

    # TRAIN
    for train in train_results:

        price = train.get("price")

        if isinstance(price, (int, float)):

            options.append({
                "type": "🚆 TRAIN",
                "price": price,
                "details": train
            })

    # FLIGHT
    for flight in flight_results:

        price = flight.get("price")

        if isinstance(price, (int, float)):

            options.append({
                "type": "✈️ FLIGHT",
                "price": price,
                "details": flight
            })

    print("\n")
    print("=" * 70)
    print("💰 TRANSPORT PRICE COMPARISON")
    print("=" * 70)

    if not options:

        print("\n❌ No transport price available.")

        return None

    cheapest_by_type = {}

    for option in options:

        transport_type = option["type"]

        if (
            transport_type not in cheapest_by_type
            or
            option["price"]
            < cheapest_by_type[transport_type]["price"]
        ):

            cheapest_by_type[transport_type] = option

    for option in cheapest_by_type.values():

        print(
            f"{option['type']:<15}"
            f"₹{option['price']:,.0f}"
        )

    cheapest = min(
        cheapest_by_type.values(),
        key=lambda x: x["price"]
    )

    print("\n" + "=" * 70)
    print("🏆 CHEAPEST OPTION")
    print("=" * 70)

    print(
        f"\n{cheapest['type']}"
    )

    print(
        f"💰 Price: ₹{cheapest['price']:,.0f}"
    )

    print(
        "\n💡 TripPilot recommends this option "
        "based on price."
    )

    print("\n" + "-" * 70)
    print("💵 PRICE DIFFERENCE")
    print("-" * 70)

    for option in cheapest_by_type.values():

        if option["type"] != cheapest["type"]:

            difference = (
                option["price"]
                - cheapest["price"]
            )

            print(
                f"{option['type']}: "
                f"₹{difference:,.0f} more expensive"
            )

    return cheapest