from validate import Validation

# note: testnest addresses are not valid using this library
def btc_addr_is_valid(addr):
  return Validation.is_btc_address(addr)