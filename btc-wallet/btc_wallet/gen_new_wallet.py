from mnemonic import Mnemonic
from bip32 import BIP32, HARDENED_INDEX
from pycoin.symbols.btc import network

### Generate seed, passphrase optional (BIP-39)
yn = input("Would you like to include a passphrase for your wallet? (y/n)")
passphr = ""
if yn == 'y':
  passphr = input(f"Set your passphrase. Make it unique but memorable!\n")
mnemo = Mnemonic("english")
words = mnemo.generate(strength=128)
bin_seed = mnemo.to_seed(words, passphrase=passphr)
entropy_byte_arr = mnemo.to_entropy(words)
readable_entr = ''.join('{:02x}'.format(x) for x in entropy_byte_arr)

print(f"\nWRITE DOWN THE FOLLOWING WORDS TO BACKUP YOUR WALLET! DO NOT FORGET THESE!")
print("*" * 20)
print(words)
print("*" * 20)

print(f'\nThe binary seed from the mnemonic is: {bin_seed.hex()}')
print(f'\nEntropy = {readable_entr}')

### Create the HD wallet (BIP-32)
wallet = BIP32.from_seed(bin_seed)
xprv = wallet.get_xpriv_from_path([HARDENED_INDEX, 1])
print(xprv)

key = network.parse.bip32(xprv)
print(key.address())