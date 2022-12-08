from mnemonic import Mnemonic
from bip32 import BIP32, HARDENED_INDEX
from pycoin.symbols.btc import network
from os.path import expanduser, dirname
from os import makedirs

class WalletManager():
  seedfile = expanduser('~/.wallet/seed.txt')

  def __init__(self):
    try:
      with open(self.seedfile,'rb') as file:
        seed = file.read()
        # Create the HD wallet (BIP-32)
        self.wallet = BIP32.from_seed(seed)
    except FileNotFoundError:
      makedirs(dirname(self.seedfile))
      print("No existing wallet found - you will need to generate a new one or recover from a seed phrase")
  
  def get_addr(self):
    xprv = self.wallet.get_xpriv_from_path([HARDENED_INDEX,1])
    key = network.parse.bip32(xprv)
    return key.address()

  def recover(self, words, passphrase):
    mnemo = Mnemonic("english")
    bin_seed = mnemo.to_seed(words, passphrase=passphrase)
    with open(self.seedfile,'wb+') as file:
      file.write(bin_seed)
    self.wallet = BIP32.from_seed(bin_seed)

  def generate(self):
    # Generate seed, passphrase optional (BIP-39)
    yn = input("Would you like to include a passphrase for your wallet? (y/n)")
    passphr = ""
    if yn == 'y':
      passphr = input(f"Set your passphrase. Make it unique but memorable!\n")
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=128)
    bin_seed = mnemo.to_seed(words, passphrase=passphr)
    # save to hidden file
    with open(self.seedfile,'wb+') as file:
      file.write(bin_seed)
    self.wallet = BIP32.from_seed(bin_seed)
    # entropy data
    entropy_byte_arr = mnemo.to_entropy(words)
    readable_entr = ''.join('{:02x}'.format(x) for x in entropy_byte_arr)

    print(f"\nWRITE DOWN THE FOLLOWING WORDS TO BACKUP YOUR WALLET! DO NOT FORGET THESE!")
    print("*" * 20)
    print(words)
    print("*" * 20)

    print(f'\nThe binary seed from the mnemonic is: {bin_seed.hex()}')
    print(f'\nEntropy = {readable_entr}')