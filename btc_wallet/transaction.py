from dataclasses import dataclass, field


class TransactionInfo:
    def __init__(self, txid, amount, fee, confirmed, block_height):
        self.txid = txid
        self.amount = amount
        self.fee = fee
        self.confirmed = confirmed
        self.block_height = block_height

    def __str__(self):
        return f"TXID: {self.txid}, Amount: {self.amount}, Fee: {self.fee}, Confirmed: {self.confirmed}, Block Height: {self.block_height}"


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

    def __init__(
        self,
        txid: str,
        to_addr: str,
        amount: int,
        fee: int,
        confirmed: bool,
        block_height: int,
    ) -> None:
        self.txid = txid
        self.to_addr = to_addr
        self.amount = amount
        self.fee = fee
        self.confirmed = confirmed
        self.block_height = block_height
