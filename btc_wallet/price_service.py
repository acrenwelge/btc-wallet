import logging

import requests


def get_btc_price(currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["bitcoin"][currency.lower()]
    else:
        logging.error(
            f"Failed to retrieve price data from CoinGecko API. Status code: {response.status_code}"
        )
        return None


def get_supported_currencies():
    url = "https://api.coingecko.com/api/v3/simple/supported_vs_currencies"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logging.error(
            f"Failed to retrieve supported currencies from CoinGecko API. Status code: {response.status_code}"
        )
        return None
