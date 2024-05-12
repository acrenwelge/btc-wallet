from btc_wallet.application_context import ApplicationContext
from btc_wallet.menus.generic import generic_menu
from btc_wallet.util import UIStrings

settings = ApplicationContext.get_user_settings()
back_to_settings_menu = "(Back to settings menu)"


def edit_currency():
    def set_valid_currency(new_currency):
        settings.currency = new_currency

    generic_menu(
        [
            ("USD", lambda: set_valid_currency("USD")),
            ("EUR", lambda: set_valid_currency("EUR")),
            (back_to_settings_menu, lambda: None),
        ],
        "Currency",
        f"Current setting: {settings.currency}",
    )


def edit_language():
    def set_valid_language(new_language):
        settings.language = new_language

    generic_menu(
        [
            ("English", lambda: set_valid_language("en")),
            ("Spanish", lambda: set_valid_language("es")),
            (back_to_settings_menu, lambda: None),
        ],
        "Language",
        f"Current setting: {settings.language}",
    )


def edit_theme():
    def set_valid_theme(new_theme):
        settings.theme = new_theme

    generic_menu(
        [
            ("Light", lambda: set_valid_theme("light")),
            ("Dark", lambda: set_valid_theme("dark")),
            ("System", lambda: set_valid_theme("system")),
            (back_to_settings_menu, lambda: None),
        ],
        "Theme",
        f"Current setting: {settings.theme}",
    )


def edit_fee_type():
    def set_valid_fee_type(new_fee_type):
        settings.fee_type = new_fee_type

    generic_menu(
        [
            ("Low", lambda: set_valid_fee_type("low")),
            ("Normal", lambda: set_valid_fee_type("normal")),
            ("Priority", lambda: set_valid_fee_type("priority")),
            (back_to_settings_menu, lambda: None),
        ],
        "Fee Type",
        f"Current setting: {settings.fee_type}",
    )


def edit_address_type():
    def set_valid_address_type(new_address_type):
        settings.address_type = new_address_type

    generic_menu(
        [
            ("Segwit", lambda: set_valid_address_type("segwit")),
            ("Bech32", lambda: set_valid_address_type("bech32")),
            ("Legacy", lambda: set_valid_address_type("legacy")),
            (back_to_settings_menu, lambda: None),
        ],
        "Address Type",
        f"Current setting: {settings.address_type}",
    )


def edit_unit():
    def set_valid_unit(new_unit):
        settings.unit = new_unit

    generic_menu(
        [
            ("BTC", lambda: set_valid_unit("BTC")),
            ("mBTC", lambda: set_valid_unit("mBTC")),
            ("sats", lambda: set_valid_unit("sats")),
            (back_to_settings_menu, lambda: None),
        ],
        "Unit",
        f"Current setting: {settings.unit}",
    )


def edit_confirmations():
    def set_valid_confirmations(new_confirmations):
        settings.confirmations = new_confirmations

    generic_menu(
        [
            ("0", lambda: set_valid_confirmations(0)),
            ("1", lambda: set_valid_confirmations(1)),
            ("2", lambda: set_valid_confirmations(2)),
            ("3", lambda: set_valid_confirmations(3)),
            ("4", lambda: set_valid_confirmations(4)),
            ("5", lambda: set_valid_confirmations(5)),
            ("6", lambda: set_valid_confirmations(6)),
            (back_to_settings_menu, lambda: None),
        ],
        "Confirmations",
        f"Current setting: {settings.confirmations}",
    )


def settings_menu():
    menu_options = [
        ("Change currency", edit_currency),
        ("Change language", edit_language),
        ("Change theme", edit_theme),
        ("Change fee type", edit_fee_type),
        ("Change address type", edit_address_type),
        ("Change unit", edit_unit),
        ("Change confirmations", edit_confirmations),
        ("Back to main menu", lambda: None),
    ]

    generic_menu(menu_options, UIStrings.SETTINGS_MENU)
