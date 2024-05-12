import logging
from getpass import getpass

from blessed import Terminal
from cryptography.fernet import InvalidToken

from btc_wallet.application_context import ApplicationContext, Modes
from btc_wallet.blockchain_client import lookup_balance
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.menus.contacts import ContactMenu
from btc_wallet.menus.generic import generic_menu
from btc_wallet.menus.send_transactions import SendTransactionsMenu
from btc_wallet.menus.settings import settings_menu
from btc_wallet.menus.view_transactions import ViewTransactionsMenu
from btc_wallet.menus.wallet import WalletMenu
from btc_wallet.tx_service import TxService
from btc_wallet.util import (
    UIStrings,
    get_keypress,
    get_user_input,
    on_shutdown,
    press_any_key_to_return,
    sats_to_btc,
)
from btc_wallet.wallet_mgr import WalletManager


class Main:

    def __init__(
        self,
        app_ctx: ApplicationContext,
        cm: ContactManager,
        wm: WalletManager,
        tx_service: TxService,
    ):
        self.app_ctx = app_ctx
        self.cm = cm
        self.wm = wm
        self.tx_service = tx_service

    def start(self):
        t = self.app_ctx.get_terminal()
        mode = self.app_ctx.get_mode()
        logging.info(f"Starting app in {mode.value} mode...")
        # Initialize menus
        wallet_menu = WalletMenu(t, self.wm)
        contact_menu = ContactMenu(t, self.cm, mode)
        view_txs_menu = ViewTransactionsMenu(self.app_ctx, self.tx_service, self.wm)
        tx_send_menu = SendTransactionsMenu(t, self.cm, self.wm)
        # Login
        success = self.login(t)
        if success:
            self.main_menu(wallet_menu, contact_menu, view_txs_menu, tx_send_menu)
        else:
            logging.error("Login failed - quitting")
        on_shutdown(t)

    def login(self, t: Terminal) -> bool:
        if not self.wm.seedfile_exists():
            print(
                """
    *******************************************************************************
    WARNING: No existing wallet found - you will need to generate a new one or
    recover from a seed phrase
    *******************************************************************************
    """
            )
            print("Press any key to continue")
            get_keypress(t)
            return True
        tries = 3
        while tries > 0:
            pw = getpass()
            try:
                self.wm.load_seed(pw)
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

    def main_menu(
        self,
        wallet_menu: WalletMenu,
        contact_menu: ContactMenu,
        view_txs_menu: ViewTransactionsMenu,
        tx_send_menu: SendTransactionsMenu,
    ):
        menu_options = [
            ("Bitcoin wallet", wallet_menu.show),
            ("Manage contact list", contact_menu.show),
            ("Lookup bitcoin address", self.lookup_address),
            ("View bitcoin transactions", view_txs_menu.show),
            ("Send bitcoin", tx_send_menu.show),
            ("Change settings", settings_menu),
            ("Quit", lambda: None),
        ]
        generic_menu(menu_options, UIStrings.MAIN_MENU)

    def lookup_address(self):
        mode = self.app_ctx.get_mode()
        t = self.app_ctx.get_terminal()
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
