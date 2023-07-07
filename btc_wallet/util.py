from .validate import Validation
from enum import Enum

class Modes(Enum):
  TEST="test"
  PROD="prod"

# note: testnest addresses are not valid using this library
def btc_addr_is_valid(addr, mode: Modes):
  if mode == Modes.PROD:
    try:
      return Validation.is_btc_address(addr)
    except ValueError:
      return False
  else:
    # TODO: implement testnet validation
    return True

SATS_PER_BTC = 100_000_000

def sats_to_btc(sats: int):
  return sats / SATS_PER_BTC