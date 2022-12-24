from mnemonic import Mnemonic
from bip32 import BIP32, HARDENED_INDEX
from bit import Key, PrivateKeyTestnet
from os.path import expanduser, dirname
from os import makedirs
from .util import Modes

class WalletManager:

  def __init__(self, mode: Modes):
    prodseedfile = expanduser('~/.wallet/seed.txt')
    testseedfile = expanduser('~/.wallet/testseed.txt')
    self.mode = mode
    self.seedfile = None
    self.hdwallet, self.keyidx = [None, None]
    if mode == Modes.PROD:
      self.seedfile = prodseedfile
    elif mode == Modes.TEST:
      self.seedfile = testseedfile
    try:
      with open(self.seedfile,'rb') as file:
        seed = file.read()
        # Create the HD wallet (BIP-32)
        self.hdwallet = BIP32.from_seed(seed)
        self.keyidx = 1
    except FileNotFoundError:
      makedirs(dirname(self.seedfile), exist_ok=True)
      print("No existing wallet found - you will need to generate a new one or recover from a seed phrase")
  
  def get_addr(self):
    return self.get_prvkey().address

  def get_wif(self):
    return self.get_prvkey().to_wif()

  def get_prvkey(self) -> Key | PrivateKeyTestnet:
    if not self.has_wallet():
      return None
    xprv = self.hdwallet.get_privkey_from_path([HARDENED_INDEX,self.keyidx])
    if self.mode == Modes.PROD:
      return Key.from_hex(xprv.hex())
    elif self.mode == Modes.TEST:
      return PrivateKeyTestnet.from_hex(xprv.hex())

  def recover(self, words, passphrase):
    if self.has_wallet():
      print("ERROR: wallet already exists, cannot recover new wallet")
      return
    mnemo = Mnemonic("english")
    bin_seed = mnemo.to_seed(words, passphrase=passphrase)
    with open(self.seedfile,'wb+') as file:
      file.write(bin_seed)
    self.hdwallet = BIP32.from_seed(bin_seed)

  def has_wallet(self):
    return self.hdwallet is not None

  def generate(self):
    if self.has_wallet():
      print("ERROR: wallet already exists, cannot generate new wallet")
      return
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
    self.hdwallet = BIP32.from_seed(bin_seed)
    # entropy data
    entropy_byte_arr = mnemo.to_entropy(words)
    readable_entr = ''.join('{:02x}'.format(x) for x in entropy_byte_arr)

    print(f"""
    INSTRUCTIONS: WRITE DOWN THE FOLLOWING WORDS TO BACKUP YOUR WALLET AND STORE IN A SAFE AND SECURE OFFLINE LOCATION.
    THIS BACKUP PHRASE WILL NOT BE SAVED ANYWHERE ON THIS DEVICE. FAILURE TO SECURE THIS BACKUP SEED PHRASE MAY CAUSE YOU TO LOSE YOUR BITCOIN.
    DO NOT FORGET THESE!""")
    print("*" * 20)
    print(words)
    print("*" * 20)

    print(f'\nThe binary seed from the mnemonic is: {bin_seed.hex()}')
    print(f'Entropy = {readable_entr}\n')