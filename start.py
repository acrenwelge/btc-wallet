import logging
from argparse import ArgumentParser

from btc_wallet.application_context import ApplicationContext
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.menus.contacts import ContactMenu
from btc_wallet.menus.main import MainMenu
from btc_wallet.menus.send_transactions import SendTransactionsMenu
from btc_wallet.menus.view_transactions import ViewTransactionsMenu
from btc_wallet.menus.wallet import WalletMenu
from btc_wallet.tx_service import TxService
from btc_wallet.util import Modes
from btc_wallet.wallet_mgr import WalletManager


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.FileHandler("wallet.log"),
        ],
    )
    console_handler = logging.getLogger().handlers[0]
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)


def configure_and_start():
    setup_logging()
    logging.debug("Starting up")
    parser = ArgumentParser()
    parser.add_argument(
        "--mode", "-m", type=Modes, default="test", help="Specify 'test' or 'prod' mode"
    )
    args = parser.parse_args()
    logging.debug(f"Arguments parsed: {args}")
    if args.mode not in [Modes.PROD, Modes.TEST]:
        raise ValueError('Mode must be either "test" or "prod"')
    # Configure application objects
    ApplicationContext._mode = args.mode
    contact_mgr = ContactManager(mode=args.mode)
    wallet_mgr = WalletManager(mode=args.mode)
    tx_service = TxService(mode=args.mode)
    # Initialize menus
    t = ApplicationContext.get_terminal()
    wallet_menu = WalletMenu(t, wallet_mgr)
    contact_menu = ContactMenu(t, contact_mgr, args.mode)
    view_txs_menu = ViewTransactionsMenu(ApplicationContext, tx_service, wallet_mgr)
    tx_send_menu = SendTransactionsMenu(t, contact_mgr, wallet_mgr)
    main_menu = MainMenu(
        contact_mgr,
        wallet_mgr,
        tx_service,
        wallet_menu,
        contact_menu,
        view_txs_menu,
        tx_send_menu,
    )
    ApplicationContext._main_menu = main_menu
    logging.debug("Objects configured. Starting main loop...")
    main_menu.start()


if __name__ == "__main__":
    configure_and_start()
