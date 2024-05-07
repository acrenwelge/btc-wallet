import requests

from btc_wallet.util import Modes


def lookup_balance(mode, address_or_xpub):
    base_url = None
    if mode == Modes.TEST:
        base_url = "https://blockstream.info/testnet/api"
    elif mode == Modes.PROD:
        base_url = "https://blockstream.info/api"
    url = f"{base_url}/address/{address_or_xpub}/utxo"
    response = requests.get(url)
    if response.status_code == 200:
        utxos = response.json()
        balance = sum(utxo["value"] for utxo in utxos)
        return balance
    else:
        print(f"Failed to retrieve balance. Status code: {response.status_code}")
        return None
