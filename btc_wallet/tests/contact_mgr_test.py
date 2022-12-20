import unittest
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.contact import Contact

class ContactManagerTest(unittest.TestCase):
  cmgr = ContactManager()

  def testAddContact(self):
    initsize = len(self.cmgr.contacts)
    self.cmgr.add_contact(Contact('abc',['1btcaddr','2btcaddr']))
    self.assertEquals(initsize+1, len(self.cmgr.contacts))

  def testGetContact(self):
    size = len(self.cmgr.contacts)
    contact1 = self.cmgr.get_contact(size)
    contact2 = self.cmgr.contacts[size-1]
    self.assertEquals(contact1, contact2)
    contact1 = self.cmgr.get_contact(1)
    contact2 = self.cmgr.contacts[0]
    self.assertEquals(contact1, contact2)