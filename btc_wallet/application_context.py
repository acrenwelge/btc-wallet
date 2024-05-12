from enum import Enum

from blessed import Terminal

from btc_wallet.user_settings import UserSettings


class Modes(Enum):
    TEST = "test"
    PROD = "prod"


class ApplicationContext:
    _terminal = None
    _user_settings = None
    _mode = None

    @classmethod
    def get_terminal(cls):
        if cls._terminal is None:
            cls._terminal = Terminal()
        return cls._terminal

    @classmethod
    def get_user_settings(cls):
        if cls._user_settings is None:
            cls._user_settings = UserSettings()
        return cls._user_settings

    @classmethod
    def set_mode(cls, mode: Modes):
        cls._mode = mode

    @classmethod
    def get_mode(cls):
        return cls._mode
