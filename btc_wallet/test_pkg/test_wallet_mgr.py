import unittest
from bit import PrivateKeyTestnet
from btc_wallet.wallet_mgr import WalletManager
from btc_wallet.util import btc_addr_is_valid, Modes

class WalletManagerTest(unittest.TestCase):

  def setUp(self) -> None:
    self.wm = WalletManager(Modes.TEST)

  @unittest.skip("need to fix validation to allow testnet addresses conditionally")
  def test_get_addr(self):
    a = self.wm.get_addr()
    self.assertTrue(btc_addr_is_valid(a))

  def test_key_in_prod_vs_test_mode(self):
    k = self.wm.get_prvkey()
    self.assertIsInstance(k, PrivateKeyTestnet)