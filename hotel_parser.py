import re


def extract_prices(text):

    prices = re.findall(r'₹\s?[\d,]+', text)

    prices = [
        int(price.replace("₹", "").replace(",", "").strip())
        for price in prices
    ]

    return prices


def parse_hotel_result(result):

    title = result.get("title", "")
    url = result.get("url", "")
    content = result.get("content", "")

    prices = extract_prices(content)

    hotel = {
        "title": title,
        "url": url,
        "prices_found": prices,
        "content": content
    }

    return hotel