from enum import Enum

from blessed import Terminal

from .validate import Validation


class Modes(Enum):
    TEST = "test"
    PROD = "prod"


def press_any_key_to_return(term: Terminal, prompt: str = ""):
    with term.location(0, term.height - 1):
        print(term.bold_reverse("Press any key to return " + prompt))
    term.inkey()


""" Prints prompt and gathers user input from the terminal starting at specified line number from top of screen
"""


def get_user_input(term: Terminal, line: int, prompt: str) -> str:
    res = ""
    while True:
        with term.location(0, line):
            print(prompt)
            print(res)
        key = term.inkey()
        if key.isalnum() or key == " ":
            res += key
        elif key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
            res = res[:-1]
        elif key.name == "KEY_ENTER":
            return res


# Modes.TEST used for validating testnet addresses
# Modes.PROD used for validating mainnet addresses
# Providing a mainnet address with Modes.TEST should return False, vice versa for testnet addresses
def btc_addr_is_valid(addr: str, mode: Modes):
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


SATS_PER_BTC = 100_000_000


def sats_to_btc(sats: int):
    return sats / SATS_PER_BTC
