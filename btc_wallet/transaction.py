from dataclasses import dataclass, field

@dataclass
class Transaction:
    txid: str
    to_addr: str
    amount: int
    fee: int
    confirmed: bool
    block_height: int
    
    def __str__(self):
      return f"Transaction ID: {self.txid}"
    
    def __init__(self, txid: str, to_addr: str, amount: int, fee: int, confirmed: bool, block_height: int) -> None:
        self.txid = txid
        self.to_addr = to_addr
        self.amount = amount
        self.fee = fee
        self.confirmed = confirmed
        self.block_height = block_height