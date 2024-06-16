import logging

from blessed import Terminal

from btc_wallet.application_context import ApplicationContext, Modes

from .validate import Validation

settings = ApplicationContext.get_user_settings()


""" UI UTILITIES """


class UIStrings:
    MAIN_MENU = "MAIN MENU"
    WALLET_MENU = "WALLET MENU"
    CONTACT_MENU = "CONTACT MENU"
    TX_SEND_MENU = "SEND BITCOIN"
    SETTINGS_MENU = "USER SETTINGS"

    @classmethod
    def to_menu(cls, menu_name: str):
        return f"to the {menu_name.lower()}"


def print_with_theme(term: Terminal, text: str):
    """Prints text using the current theme"""
    if settings.theme == "dark":
        print(term.white_on_midnightblue + text)
    else:
        print(term.midnightblue_on_white + text)


def press_any_key_to_return(term: Terminal, prompt: str = ""):
    with term.location(0, term.height - 1):
        print(term.bold_reverse("Press any key to return " + prompt))
    key = get_keypress(term)
    if not key:
        logging.warn("Logging out due to inactivity")
        on_shutdown(term)


def get_keypress(term: Terminal):
    """Gets a Keystroke from terminal using a default timeout \n
    All `.inkey()` calls should be wrapped by this function to ensure consistency
    """
    return term.inkey(timeout=60)


def get_user_input(term: Terminal, line: int, prompt: str) -> str:
    """Prints prompt and gathers user input from the terminal starting at specified line number from top of screen"""
    res = ""
    while True:
        with term.location(0, line):
            print(prompt)
            print(res)
        key = get_keypress(term)
        if key.isalnum() or key == " ":
            res += key
        elif key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
            res = res[:-1]
        elif key.name == "KEY_ENTER":
            return res
        elif not key:
            logging.warn("Logging out due to inactivity")
            quit()


"""" VALIDATION UTILITIES """


def btc_addr_is_valid(addr: str, mode: Modes):
    """Check if a Bitcoin address is valid for the specified mode (testnet or prod). \n
    `Modes.TEST` used for validating testnet addresses. \n
    `Modes.PROD` used for validating mainnet addresses. \n
    Providing a mainnet address with `Modes.TEST` should return `False`, vice versa for testnet addresses
    """
    if mode == Modes.PROD:
        try:
            return Validation.is_btc_address(addr)
        except ValueError:
            return False
    else:
        addr_type = Validation.get_btc_addr_type(addr)
        return addr_type is not None and addr_type.startswith("testnet")


def get_btc_addr_type(addr):
    return Validation.get_btc_addr_type(addr)


""" LIFECYCLE UTILITIES """


def on_shutdown(term: Terminal):
    """Called when exiting all menus and the application is shutting down.
    Saves any necessary data and performs cleanup tasks
    """
    logging.info("Shutting down...")
    settings.save_settings()
    print(term.clear())
    quit()


""" CONVERSIONS"""

SATS_PER_BTC = 100_000_000


def sats_to_btc(sats: int):
    return sats / SATS_PER_BTC
