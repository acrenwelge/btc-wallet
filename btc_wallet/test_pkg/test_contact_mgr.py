import unittest
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.contact import Contact

class ContactManagerTest(unittest.TestCase):
  cmgr = ContactManager()

  def test_add_contact(self):
    initsize = len(self.cmgr.contacts)
    self.cmgr.add_contact(Contact('abc',['1btcaddr','2btcaddr']))
    self.assertEqual(initsize+1, len(self.cmgr.contacts))

  def test_get_contact(self):
    size = len(self.cmgr.contacts)
    contact1 = self.cmgr.get_contact(size)
    contact2 = self.cmgr.contacts[size-1]
    self.assertEqual(contact1, contact2)
    contact1 = self.cmgr.get_contact(1)
    contact2 = self.cmgr.contacts[0]
    self.assertEqual(contact1, contact2)

if __name__ == '__main__':
    unittest.main()