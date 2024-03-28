from enum import Enum

from .validate import Validation


class Modes(Enum):
    TEST = "test"
    PROD = "prod"


# Modes.TEST used for validating testnet addresses
# Modes.PROD used for validating mainnet addresses
# Providing a mainnet address with Modes.TEST should return False, vice versa for testnet addresses
def btc_addr_is_valid(addr, mode: Modes):
    if mode == Modes.PROD:
        try:
            return Validation.is_btc_address(addr)
        except ValueError:
            return False
    else:
        return Validation.get_btc_addr_type(addr).startswith("testnet")


def get_btc_addr_type(addr):
    return Validation.get_btc_addr_type(addr)


SATS_PER_BTC = 100_000_000


def sats_to_btc(sats: int):
    return sats / SATS_PER_BTC
