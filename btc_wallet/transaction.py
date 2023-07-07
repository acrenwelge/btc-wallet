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