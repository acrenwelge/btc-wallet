import logging
from argparse import ArgumentParser

from btc_wallet.application_context import ApplicationContext
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.menus.main import Main
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
    ApplicationContext.set_mode(args.mode)
    contact_mgr = ContactManager(mode=args.mode)
    wallet_mgr = WalletManager(mode=args.mode)
    tx_service = TxService(mode=args.mode)
    Main(ApplicationContext, contact_mgr, wallet_mgr, tx_service).start()


if __name__ == "__main__":
    configure_and_start()
