import json
import logging
from os.path import expanduser


class UserSettings:
    def __init__(self) -> None:
        try:
            self.load_settings()
        except FileNotFoundError:
            self.set_defaults()
            self.save_settings()  # Save default settings if none found

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, new_currency):
        # TODO: Define list of valid currencies
        if new_currency not in ["USD", "EUR", "GBP"]:
            raise ValueError("Invalid currency")
        self._currency = new_currency

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, new_language):
        if new_language not in ["en", "es"]:
            raise ValueError("Invalid language")
        self._language = new_language

    @property
    def theme(self):
        return self._theme

    @theme.getter
    def theme(self):
        if self._theme == "system":
            return self.get_system_theme()
        return self._theme

    @theme.setter
    def theme(self, new_theme):
        """Set the theme for the application"""
        if new_theme not in ["light", "dark", "system"]:
            raise ValueError("Invalid theme")
        self._theme = new_theme

    def get_system_theme(self):
        import platform

        if platform.system() == "Windows":
            # Check Windows registry for dark mode setting
            try:
                import ctypes

                value = ctypes.windll.winreg.OpenKey(
                    ctypes.windll.winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                    0,
                    ctypes.windll.winreg.KEY_READ,
                )
                registry_value, _ = ctypes.windll.winreg.QueryValueEx(
                    value, "AppsUseLightTheme"
                )
                if registry_value == 0:
                    return "dark"
                else:
                    return "light"
            except Exception as e:
                print("Error reading Windows registry:", e)
        elif platform.system() == "Darwin":  # macOS
            # Check macOS system preferences for appearance
            try:
                from Foundation import NSUserDefaults

                if (
                    NSUserDefaults.standardUserDefaults().stringForKey_(
                        "AppleInterfaceStyle"
                    )
                    == "Dark"
                ):
                    return "dark"
                else:
                    return "light"
            except Exception as e:
                print("Error reading macOS preferences:", e)
        elif platform.system() == "Linux":
            # Check for Linux environment variable or configuration file
            # (Implementation may vary depending on the Linux distribution)
            # Example: Check for GTK theme settings
            try:
                import os

                if os.environ.get("GTK_THEME", "").endswith(":dark"):
                    return "dark"
                else:
                    return "light"
            except Exception as e:
                print("Error reading Linux environment variables:", e)
        else:
            # Unsupported platform
            print("Unsupported platform:", platform.system())
        return "light"  # default if unable to determine

    @property
    def fee_type(self):
        return self._fee_type

    @fee_type.setter
    def fee_type(self, new_fee_type):
        if new_fee_type not in ["low", "normal", "priority"]:
            raise ValueError("Invalid fee type")
        self._fee_type = new_fee_type

    @property
    def address_type(self):
        return self._address_type

    @address_type.setter
    def address_type(self, new_address_type):
        if new_address_type not in ["segwit", "bech32", "legacy"]:
            raise ValueError("Invalid address type")
        self._address_type = new_address_type

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_unit):
        if new_unit not in ["BTC", "mBTC", "sats"]:
            raise ValueError("Invalid unit")
        self._unit = new_unit

    @property
    def confirmations(self):
        return self._confirmations

    @confirmations.setter
    def confirmations(self, new_confirmations: int):
        if new_confirmations < 0 or new_confirmations > 6:
            raise ValueError("Confirmations must be between 0 and 6")
        self._confirmations = new_confirmations

    def load_settings(self):
        with open(expanduser("~/.wallet/settings.json"), "r") as f:
            settings = json.load(f)
            self._currency = settings["currency"]
            self._language = settings["language"]
            self._theme = settings["theme"]
            self._fee_type = settings["fee_type"]
            self._address_type = settings["address_type"]
            self._unit = settings["unit"]
            self._confirmations = settings["confirmations"]

    def set_defaults(self):
        self._currency = "USD"
        self._language = "en"
        self._theme = "light"
        self._fee_type = "normal"
        self._address_type = "segwit"
        self._unit = "BTC"
        self._confirmations = "6"

    def to_dict(self):
        return {
            "currency": self.currency,
            "language": self.language,
            "theme": self.theme,
            "fee_type": self.fee_type,
            "address_type": self.address_type,
            "unit": self.unit,
            "confirmations": self.confirmations,
        }

    def save_settings(self):
        settings = self.to_dict()
        try:
            with open(expanduser("~/.wallet/settings.json"), "w") as f:
                f.write(json.dumps(settings))
        except IOError:
            logging.error("Error saving settings")
