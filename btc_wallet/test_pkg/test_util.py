import unittest
from unittest.mock import MagicMock, Mock, patch

import btc_wallet.util


class UtilTest(unittest.TestCase):
    term = MagicMock()

    def test_get_keypress(self):
        # wait for timeout
        with patch("btc_wallet.util.get_keypress", return_value=""):
            res = btc_wallet.util.get_keypress(self.term)
            self.assertEqual(res, "")

    def test_get_user_input(self):
        with patch("btc_wallet.util.get_user_input", return_value=""):
            res = btc_wallet.util.get_user_input(self.term, 0, "test")
            self.assertEqual(res, "")


if __name__ == "__main__":
    unittest.main()
