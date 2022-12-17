from coinage import BitcoinBlockchain, FailedValidation, FailedChecksumValidation

btc_validation = BitcoinBlockchain()

def btc_addr_is_valid(addr):
  try:
    valid = btc_validation.validate(addr)
    if valid.is_from_main_net():
      return True
    else:
      print('ERROR: this is not a mainnet address')
  except FailedChecksumValidation:
    print('ERROR: failed checksum: you probably made a mistake when copying this address')
  except FailedValidation:
    print('ERROR: this is not a valid bitcoin address') 
  return False