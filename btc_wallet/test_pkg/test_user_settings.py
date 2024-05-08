import unittest

from btc_wallet.user_settings import UserSettings


class UserSettingsTest(unittest.TestCase):

    def test_load_default_settings(self):
        user_settings = UserSettings()
        self.assertEqual(user_settings.currency, "USD")
        self.assertEqual(user_settings.language, "en")
        self.assertEqual(user_settings.user_settings["theme"], "light")
        self.assertEqual(user_settings.user_settings["fee_type"], "normal")
        self.assertEqual(user_settings.user_settings["address_type"], "segwit")
        self.assertEqual(user_settings.user_settings["unit"], "BTC")
        self.assertEqual(user_settings.user_settings["confirmations"], "6")

    def test_change_setting(self):
        user_settings = UserSettings()
        user_settings.currency = "EUR"
        self.assertEqual(user_settings.currency, "EUR")

    def test_invalid_change_setting(self):
        user_settings = UserSettings()
        with self.assertRaises(ValueError):
            user_settings.currency = "BLAH"


if __name__ == "__main__":
    unittest.main()
