import unittest

from btc_wallet.contact import Contact
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.util import Modes


class ContactManagerTest(unittest.TestCase):
    cmgr_test = ContactManager(Modes.TEST)
    cmgr_prod = ContactManager(Modes.PROD)

    def test_add_contact_testmode(self):
        initsize = len(self.cmgr_test.contacts)
        self.cmgr_test.add_contact(Contact(initsize + 1, "abc", "1btcaddr"))
        self.assertEqual(initsize + 1, len(self.cmgr_test.contacts))

    def test_add_contact_prodmode(self):
        initsize = len(self.cmgr_prod.contacts)
        self.cmgr_prod.add_contact(Contact(initsize + 1, "abc", "1btcaddr"))
        self.assertEqual(initsize + 1, len(self.cmgr_prod.contacts))

    def test_get_contact_testmode(self):
        size = len(self.cmgr_test.contacts)
        contact1 = self.cmgr_test.get_contact(size + 1)
        contact2 = self.cmgr_test.contacts[size - 1]
        self.assertEqual(contact1, contact2)
        contact1 = self.cmgr_test.get_contact(1)
        contact2 = self.cmgr_test.contacts[0]
        self.assertEqual(contact1, contact2)

    def test_get_contact_prodmode(self):
        size = len(self.cmgr_prod.contacts)
        contact1 = self.cmgr_prod.get_contact(size)
        contact2 = self.cmgr_prod.contacts[size - 1]
        self.assertEqual(contact1, contact2)
        contact1 = self.cmgr_prod.get_contact(1)
        contact2 = self.cmgr_prod.contacts[0]
        self.assertEqual(contact1, contact2)


if __name__ == "__main__":
    unittest.main()
