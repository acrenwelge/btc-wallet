import logging
from getpass import getpass

from blessed import Terminal
from cryptography.fernet import InvalidToken

from btc_wallet.application_context import ApplicationContext
from btc_wallet.blockchain_client import lookup_balance
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.menus.contacts import ContactMenu
from btc_wallet.menus.generic import generic_menu
from btc_wallet.menus.send_transactions import SendTransactionsMenu
from btc_wallet.menus.settings import settings_menu
from btc_wallet.menus.view_transactions import ViewTransactionsMenu
from btc_wallet.menus.wallet import WalletMenu
from btc_wallet.price_service import get_btc_price
from btc_wallet.tx_service import TxService
from btc_wallet.util import (
    UIStrings,
    get_keypress,
    get_user_input,
    press_any_key_to_return,
    sats_to_btc,
)
from btc_wallet.wallet_mgr import WalletManager


class MainMenu:

    def __init__(
        self,
        contact_mgr: ContactManager,
        wallet_mgr: WalletManager,
        tx_service: TxService,
        wallet_menu: WalletMenu,
        contact_menu: ContactMenu,
        view_txs_menu: ViewTransactionsMenu,
        tx_send_menu: SendTransactionsMenu,
    ):
        self.contact_mgr = contact_mgr
        self.wallet_mgr = wallet_mgr
        self.tx_service = tx_service
        self.wallet_menu = wallet_menu
        self.contact_menu = contact_menu
        self.view_txs_menu = view_txs_menu
        self.tx_send_menu = tx_send_menu

    def start(self):
        t = ApplicationContext.get_terminal()
        mode = ApplicationContext.get_mode()
        logging.info(f"Starting app in {mode.value} mode...")
        # Login
        success = self.login(t)
        if success:
            self.show()
        else:
            logging.error("Login failed - quitting")
        # on_shutdown(t)

    def login(self, t: Terminal) -> bool:
        if not self.wallet_mgr.seedfile_exists():
            print(
                """
    *******************************************************************************
    WARNING: No existing wallet found - you will need to generate a new one or
    recover from a seed phrase
    *******************************************************************************
    """
            )
            print("Press any key to continue")
            with t.cbreak():
                get_keypress(t)
                return True
        tries = 3
        while tries > 0:
            pw = getpass()
            try:
                self.wallet_mgr.load_seed(pw)
                logging.info("Wallet loaded successfully")
                return True
            except InvalidToken:
                tries -= 1
                logging.error(
                    f"Incorrect password - wallet could not be loaded. {tries} more chances"
                )
                continue
        logging.info("Maximum password attempts reached")
        return False

    def show(self):
        menu_options = [
            ("Bitcoin wallet", self.wallet_menu.show),
            ("Manage contact list", self.contact_menu.show),
            ("Lookup bitcoin address", self.lookup_address),
            ("View bitcoin transactions", self.view_txs_menu.show),
            ("Send bitcoin", self.tx_send_menu.show),
            ("Bitcoin current price", self.show_fiat_price),
            ("Change settings", settings_menu),
            ("Quit", lambda: None),
        ]
        generic_menu(menu_options, UIStrings.MAIN_MENU)

    def lookup_address(self):
        t = ApplicationContext.get_terminal()
        mode = ApplicationContext.get_mode()
        with t.fullscreen():
            print(t.clear())
            addr = get_user_input(t, 1, "Enter the bitcoin address or xpub to look up:")
            sat_balance = lookup_balance(mode, addr)
            with t.location(0, 4):
                if sat_balance is not None:
                    print(f"Balance for {addr}: {sat_balance} sats")
                    print(f"Balance for {addr}: {sats_to_btc(sat_balance)} BTC")
                else:
                    print("Error retrieving balance - please try again")
            press_any_key_to_return(t, "to the main menu")
            self.show()

    def show_fiat_price(self):
        t = ApplicationContext.get_terminal()
        cur = ApplicationContext.get_user_settings().currency
        price = get_btc_price(currency=cur)
        with t.fullscreen():
            print(t.clear())
            print(f"Current price of Bitcoin: ${price}")
            press_any_key_to_return(t, "to the main menu")
            self.show()
