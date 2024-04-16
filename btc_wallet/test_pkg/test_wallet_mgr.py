import os
import unittest

import pytest
from bit import Key, PrivateKeyTestnet
from cryptography.fernet import InvalidToken

from btc_wallet.util import Modes
from btc_wallet.wallet_mgr import WalletManager


class WalletManagerTest(unittest.TestCase):

    def setUp(self) -> None:
        self.wm = WalletManager(Modes.TEST)
        self.wm.seedfile = "./unit_test_fake_seed.bin"
        self.wm.saltfile = "./unit_test_fake_salt.bin"

    def tearDown(self) -> None:
        if self.wm.seedfile_exists():
            os.remove(self.wm.seedfile)  # clean up fake binary seed file
        if self.wm.saltfile_exists():
            os.remove(self.wm.saltfile)  # clean up fake salt file

    def test_key_in_test_mode(self):
        self.wm.generate()
        self.assertTrue(self.wm.has_wallet())
        k = self.wm.get_prvkey()
        self.assertIsInstance(k, PrivateKeyTestnet)

    def test_key_in_prod_mode(self):
        self.wm = WalletManager(Modes.PROD)
        self.wm.generate()
        self.assertTrue(self.wm.has_wallet())
        k = self.wm.get_prvkey()
        self.assertIsInstance(k, Key)

    @pytest.mark.dependency()
    def test_generate_new_wallet(self):
        _, writeseed, _ = self.wm.generate()  # no passphrase and no encryption
        self.assertTrue(self.wm.has_wallet())
        self.assertTrue(self.wm.seedfile_exists())
        with open(self.wm.seedfile, "rb") as f:
            readseed = f.read()
        self.assertEqual(writeseed, readseed)

    # @pytest.mark.dependency(depends=["test_generate_new_wallet"])
    def test_recover_wallet(self):
        words, original_seed, _ = self.wm.generate()  # no passphrase and no encryption
        self.wm.wipe()
        self.wm.recover(words)
        self.assertTrue(self.wm.has_wallet())
        self.assertTrue(self.wm.seedfile_exists())
        with open(self.wm.seedfile, "rb") as f:
            newseed = f.read()
        self.assertEqual(original_seed, newseed)

    # @pytest.mark.dependency(depends=["test_generate_new_wallet"])
    def test_load_seed_unencrypted(self):
        self.wm.generate()
        self.assertTrue(self.wm.seedfile_exists())
        self.assertTrue(self.wm.load_seed())
        self.assertTrue(self.wm.has_wallet())

    # @pytest.mark.dependency(depends=["test_generate_new_wallet"])
    def test_load_seed_encrypted_valid(self):
        self.wm.generate(encryption_password="password")
        self.assertTrue(self.wm.seedfile_exists())
        self.assertTrue(self.wm.load_seed("password"))

    # @pytest.mark.dependency(depends=["test_generate_new_wallet"])
    def test_load_seed_encrypted_invalid(self):
        self.wm.generate(encryption_password="password")
        self.assertTrue(self.wm.seedfile_exists())
        with self.assertRaises(InvalidToken):
            self.wm.load_seed("wrong_password")
