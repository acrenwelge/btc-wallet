import logging
import os
from os import makedirs
from os.path import dirname, expanduser

from bip32 import BIP32, HARDENED_INDEX
from bit import Key, PrivateKeyTestnet
from mnemonic import Mnemonic

from .encrypt import decrypt_seed, encrypt_seed
from .util import Modes


class WalletAlreadyExistsError(Exception):
    pass


class WalletManager:

    hdwallet: BIP32
    seedfile: str
    saltfile: str
    mode: Modes
    keyidx: int

    def __init__(self, mode: Modes):
        self.mode = mode
        if mode == Modes.PROD:
            self.seedfile = expanduser("~/.wallet/seed.bin")
            self.saltfile = expanduser("~/.wallet/salt.bin")
        elif mode == Modes.TEST:
            self.seedfile = expanduser("~/.wallet/testseed.bin")
            self.saltfile = expanduser("~/.wallet/testsalt.bin")
        self.hdwallet, self.keyidx = None, 1

    def seedfile_exists(self):
        return os.path.exists(self.seedfile)

    def saltfile_exists(self):
        return os.path.exists(self.saltfile)

    def load_seed(self, decryption_password="") -> bool:
        """Load the seed from the seed file and initialize the BIP-32 HD wallet.
        If a decryption password is provided, the seed file will be decrypted first.
        @return True if the seed was successfully loaded, False if no seed file was found.
        Exceptions are raised if there is a problem reading from or decrypting the seed file.
        """
        if not self.seedfile_exists():
            makedirs(dirname(self.seedfile), exist_ok=True)
            logging.warning("No seed file found")
            return False
        seed = None
        with open(self.seedfile, "rb") as file:
            seed = file.read()
        if decryption_password != "":
            salt = self._get_salt()
            seed = decrypt_seed(seed, salt, decryption_password)
        self.hdwallet = BIP32.from_seed(seed)
        return True

    def get_addr(self):
        key = self.get_prvkey()
        if key is None:
            raise ValueError("No wallet found")
        return key.address

    def get_bal(self) -> int:
        return int(self.get_prvkey().get_balance())

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

    def recover(self, words, bip32_passphrase=""):
        if self.has_wallet():
            raise WalletAlreadyExistsError
        mnemo = Mnemonic("english")
        bin_seed = mnemo.to_seed(words, passphrase=bip32_passphrase)
        with open(self.seedfile, "wb+") as file:
            file.write(bin_seed)
            logging.info("Binary seed saved to file")
        self.hdwallet = BIP32.from_seed(bin_seed)
        logging.info("Wallet recovered!")

    def has_wallet(self):
        return self.hdwallet is not None

    def generate(self, bip32_passphrase: str = "", encryption_password: str = ""):
        """Uses BIP-39 to generate a new seed and save it to a file.
        Initializes the BIP-32 HD wallet with the seed.
        """
        if self.has_wallet():
            raise WalletAlreadyExistsError
        # Generate seed, passphrase optional (BIP-39)
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=128)
        bin_seed = mnemo.to_seed(words, passphrase=bip32_passphrase)
        self.hdwallet = BIP32.from_seed(bin_seed)
        # encrypt and save salt if encryption password provided
        if encryption_password != "":
            encrypted_seed, salt = encrypt_seed(bin_seed, encryption_password)
            with open(self.saltfile, "wb+") as file_out:
                file_out.write(salt)
                logging.info("Random salt saved to file")
            bin_seed = encrypted_seed
        with open(self.seedfile, "wb+") as file_out:
            file_out.write(bin_seed)
        # entropy data
        entropy_byte_arr = mnemo.to_entropy(words)
        readable_entr = "".join("{:02x}".format(x) for x in entropy_byte_arr)
        return [words, bin_seed, readable_entr]

    def wipe(self):
        if self.has_wallet():
            self.hdwallet = None
            try:
                os.remove(self.seedfile)
                os.remove(self.saltfile)
            except FileNotFoundError as e:
                logging.warning(f"No file found to delete")
            logging.info("Wallet wiped!")
        else:
            logging.error("No wallet found to wipe")

    def _get_salt(self):
        with open(self.saltfile, "rb") as file:
            return file.read()
