import unittest
from btc_wallet.util import btc_addr_is_valid, Modes
from btc_wallet.contact_mgr import ContactManager

class UtilTest(unittest.TestCase):
  cmgr = ContactManager
  addresses = []

  @classmethod
  def setUpClass(cls):
    with open('test-addresses.txt','r') as f:
      lines = f.readlines()
      for l in lines:
        addr = l.split(':')[1].strip()
        cls.addresses.append(addr)

  @unittest.skip("need to fix validation to allow testnet addresses conditionally")
  def test_validate_true(self):
    for addr in self.addresses:
      res = btc_addr_is_valid(addr)
      self.assertTrue(res)

  def test_validate_false(self):
    self.assertFalse(btc_addr_is_valid('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb', Modes.PROD))

if __name__ == '__main__':
    unittest.main()