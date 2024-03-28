import unittest

from btc_wallet.contact_mgr import ContactManager
from btc_wallet.util import Modes, btc_addr_is_valid


class AddressValidationTests(unittest.TestCase):
    cmgr = ContactManager

    def test_validate_testnet_address(self):
        addr = "mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt"
        self.assertTrue(btc_addr_is_valid(addr, Modes.TEST))

    def test_validate_mainnet_address_fails(self):
        # should fail because this is a mainnet address
        addr = "12higDjoCCNXSA95xZMWUdPvXNmkAduhWv"
        self.assertFalse(btc_addr_is_valid(addr, Modes.TEST))

    def test_validate_satoshi_address(self):
        # satoshi's address
        addr = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        self.assertTrue(btc_addr_is_valid(addr, Modes.PROD))

    @unittest.skip("P2PK not supported")
    def test_validate_p2pk_address(self):
        # P2PK address
        self.assertTrue(
            btc_addr_is_valid(
                "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f",
                Modes.PROD,
            )
        )

    def test_validate_p2pkh_address(self):
        # P2PKH address
        self.assertTrue(
            btc_addr_is_valid(
                "12higDjoCCNXSA95xZMWUdPvXNmkAduhWv",
                Modes.PROD,
            )
        )

    def test_validate_p2sh_address(self):
        # P2SH address
        self.assertTrue(
            btc_addr_is_valid("342ftSRCvFHfCeFFBuz4xwbeqnDw6BGUey", Modes.PROD)
        )

    def test_validate_p2wpkh_address(self):
        # P2WPKH address
        self.assertTrue(
            btc_addr_is_valid("bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c", Modes.PROD)
        )

    def test_validate_p2wsh_address(self):
        # P2WSH address
        self.assertTrue(
            btc_addr_is_valid(
                "bc1qeklep85ntjz4605drds6aww9u0qr46qzrv5xswd35uhjuj8ahfcqgf6hak",
                Modes.PROD,
            )
        )

    @unittest.skip("Taproot addresses not yet supported")
    def test_validate_p2tr_address(self):
        # P2TR address
        self.assertTrue(
            btc_addr_is_valid(
                "bc1pxwww0ct9ue7e8tdnlmug5m2tamfn7q06sahstg39ys4c9f3340qqxrdu9k",
                Modes.PROD,
            )
        )

    def test_validate_random_address(self):
        # randomly generated address
        self.assertTrue(
            btc_addr_is_valid("1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i", Modes.PROD)
        )

    def test_validate_random_address_fails(self):
        # randomly generated address - modified to be invalid
        self.assertFalse(
            btc_addr_is_valid("1AGNa15ZQXblahFiqJ2i7Z2DPU2J6hW62i", Modes.PROD)
        )

    def test_validate_prod_addresses_false(self):
        # satoshi's address - last character is wrong
        self.assertFalse(
            btc_addr_is_valid("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb", Modes.PROD)
        )


if __name__ == "__main__":
    unittest.main()
