import os
import unittest

import pytest
from cryptography.fernet import InvalidToken

from btc_wallet.encrypt import decrypt_seed, derive_fernet_key, encrypt_seed


class TestEncrypt(unittest.TestCase):

    def test_derive_fernet_key(self):
        password = "test_password"
        salt = os.urandom(16)
        key = derive_fernet_key(password, salt)
        self.assertEqual(len(key), 32)  # Fernet keys are 32 bytes long
        key2 = derive_fernet_key(password, salt)
        self.assertEqual(key, key2)  # prove that the key is deterministic

    def test_encrypt_decrypt_seed(self):
        data = b"This is a test message to be encrypted."
        password = "test_password"
        encrypted_seed, salt = encrypt_seed(data, password)
        result = decrypt_seed(encrypted_seed, salt, password)
        self.assertEqual(result, data)

    def test_encrypt_decrypt_seed_wrong_password(self):
        data = b"This is a test message to be encrypted."
        password = "test_password"
        encrypted_seed, salt = encrypt_seed(data, password)
        with self.assertRaises(InvalidToken):
            decrypt_seed(encrypted_seed, salt, "wrong password")
