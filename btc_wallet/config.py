import pickle
from os.path import expanduser


class Config:

    def __init__(self) -> None:
        self.user_settings = self.load_settings()

    def load_settings(self):
        try:
            with open(expanduser("~/.wallet/settings.pkl", "rb")) as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {
                "currency": "USD",
                "language": "en",
                "theme": "light",
                "fee_type": "normal",
                "address_type": "segwit",
                "unit": "BTC",
                "confirmations": "6",
            }

    # TODO: validate new setting value (use an enum for each setting type?)
    def change_setting(self, setting, new_value):
        if setting not in self.user_settings:
            raise ValueError(f"Setting {setting} not found")
        self.user_settings[setting] = new_value
        self.save_settings()

    def save_settings(self):
        with open(expanduser("~/.wallet/settings.pkl", "wb")) as f:
            pickle.dump(self.user_settings, f)
