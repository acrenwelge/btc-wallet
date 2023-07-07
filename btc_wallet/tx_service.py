import requests
from .transaction import Transaction
from btc_wallet.util import Modes

class TxService:
    
    def __init__(self, mode: Modes) -> None:
        if mode == Modes.TEST:
            self.base_url = 'https://blockstream.info/testnet/api'
        elif mode == Modes.PROD:
            self.base_url = 'https://blockstream.info/api'
    
    def get_tx(self, tx_id: str):
        resp = requests.get(self.base_url + f'/tx/{tx_id}').json()
        return Transaction(resp['txid'],
                           resp['vout'][0]['scriptpubkey_address'], 
                           resp['vout'][0]['value'],
                           resp['fee'],
                           resp['status']['confirmed'], 
                           resp['status']['block_height'])