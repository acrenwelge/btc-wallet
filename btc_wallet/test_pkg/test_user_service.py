import unittest
from unittest.mock import patch, MagicMock
from btc_wallet.user_service import UserService

class UserServiceTest(unittest.TestCase):
  mock_pw = 'randomtestpw1'
  user_serv = UserService()

  def test_password_validates_true(self):
    self.user_serv.get_pw_from_file = MagicMock(return_value=self.mock_pw)
    res = self.user_serv.validate_password(self.mock_pw)
    self.assertTrue(res)

  def test_password_validates_false(self):
    self.user_serv.get_pw_from_file = MagicMock(return_value=self.mock_pw)
    res = self.user_serv.validate_password("wrong_password")
    self.assertFalse(res)

if __name__ == '__main__':
  unittest.main()