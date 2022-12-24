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