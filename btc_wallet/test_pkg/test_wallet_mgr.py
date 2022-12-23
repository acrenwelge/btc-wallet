import unittest
from btc_wallet.wallet_mgr import WalletManager
from btc_wallet.util import btc_addr_is_valid

class WalletManagerTest(unittest.TestCase):
  wm = WalletManager()

  def test_get_addr(self):
    a = self.wm.get_addr()
    self.assertTrue(btc_addr_is_valid(a))