import logging
from os import makedirs
from os.path import dirname, expanduser

from bip32 import BIP32, HARDENED_INDEX
from bit import Key, PrivateKeyTestnet
from mnemonic import Mnemonic

from .util import Modes


class WalletAlreadyExistsError(Exception):
    pass


class WalletManager:

    hdwallet: BIP32
    seedfile: str
    mode: Modes

    def __init__(self, mode: Modes):
        prodseedfile = expanduser("~/.wallet/seed.txt")
        testseedfile = expanduser("~/.wallet/testseed.txt")
        self.mode = mode
        self.hdwallet, self.keyidx = None, 1
        if mode == Modes.PROD:
            self.seedfile = prodseedfile
        elif mode == Modes.TEST:
            self.seedfile = testseedfile
        try:
            with open(self.seedfile, "rb") as file:
                seed = file.read()
                # Create the HD wallet (BIP-32)
                self.hdwallet = BIP32.from_seed(seed)
        except FileNotFoundError:
            makedirs(dirname(self.seedfile), exist_ok=True)
            logging.warn(
                "No existing wallet found - you will need to generate a new one or recover from a seed phrase"
            )
            print(
                """
*******************************************************************************
WARNING: No existing wallet found - you will need to generate a new one or
recover from a seed phrase
*******************************************************************************
"""
            )

    def get_addr(self):
        key = self.get_prvkey()
        if key is None:
            raise ValueError("No wallet found")
        return key.address

    def get_bal(self):
        return self.get_prvkey().get_balance()

    def get_wif(self):
        return self.get_prvkey().to_wif()

    def get_prvkey(self) -> Key | PrivateKeyTestnet:
        if not self.has_wallet():
            return None
        prvkey = self.hdwallet.get_privkey_from_path([HARDENED_INDEX, self.keyidx])
        if self.mode == Modes.PROD:
            return Key.from_hex(prvkey.hex())
        elif self.mode == Modes.TEST:
            return PrivateKeyTestnet.from_hex(prvkey.hex())

    def recover(self, words, passphrase):
        if self.has_wallet():
            raise WalletAlreadyExistsError
        mnemo = Mnemonic("english")
        bin_seed = mnemo.to_seed(words, passphrase=passphrase)
        with open(self.seedfile, "wb+") as file:
            file.write(bin_seed)
            logging.info("Binary seed saved to file")
        self.hdwallet = BIP32.from_seed(bin_seed)
        logging.info("Wallet recovered!")

    def has_wallet(self):
        return self.hdwallet is not None

    def generate(self, passphrase: str):
        if self.has_wallet():
            raise WalletAlreadyExistsError
        # Generate seed, passphrase optional (BIP-39)
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=128)
        bin_seed = mnemo.to_seed(words, passphrase=passphrase)
        # save to hidden file
        with open(self.seedfile, "wb+") as file:
            file.write(bin_seed)
            logging.info("Binary seed saved to file")
        self.hdwallet = BIP32.from_seed(bin_seed)
        # entropy data
        entropy_byte_arr = mnemo.to_entropy(words)
        readable_entr = "".join("{:02x}".format(x) for x in entropy_byte_arr)
        return [words, bin_seed, readable_entr]
