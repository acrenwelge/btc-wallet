from functools import partial

from btc_wallet.application_context import ApplicationContext
from btc_wallet.menus.generic import generic_menu
from btc_wallet.util import UIStrings, press_any_key_to_return

settings = ApplicationContext.get_user_settings()
back_to_settings_menu = "(Back to settings menu)"


def make_tuple(func, arg):
    return (arg, partial(func, arg))


def display_msg(setting, new_value):
    term = ApplicationContext.get_terminal()
    print(term.clear)
    with term.location(0, term.height - 5):
        print(f"{setting} set to {new_value}")
        press_any_key_to_return(term, back_to_settings_menu)


def edit_currency():
    def set_valid_currency(new_currency):
        settings.currency = new_currency
        display_msg("Currency", new_currency)

    tuples = [
        make_tuple(set_valid_currency, cur) for cur in settings.supported_currencies()
    ]
    tuples.append((back_to_settings_menu, lambda: None))
    generic_menu(tuples, "Currency", f"Current setting: {settings.currency}")


def edit_language():
    def set_valid_language(new_language):
        settings.language = new_language
        display_msg("Language", new_language)

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
        display_msg("Theme", new_theme)

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
        display_msg("Fee Type", new_fee_type)

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
        display_msg("Address Type", new_address_type)

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
        display_msg("Unit", new_unit)

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
        display_msg("Confirmations", new_confirmations)

    tuples = [
        make_tuple(set_valid_confirmations, conf) for conf in [0, 1, 2, 3, 4, 5, 6]
    ]
    tuples.append((back_to_settings_menu, lambda: None))

    generic_menu(
        tuples,
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
