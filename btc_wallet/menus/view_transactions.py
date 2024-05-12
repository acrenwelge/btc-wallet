import logging

from prettytable import PrettyTable

from btc_wallet.application_context import ApplicationContext
from btc_wallet.transaction import TransactionInfo
from btc_wallet.tx_service import TxService
from btc_wallet.wallet_mgr import WalletManager

from ..util import UIStrings, get_keypress, on_shutdown, press_any_key_to_return


def dummy_data():
    import random

    txs = []
    init = 1234
    for _ in range(5):
        txs.append(
            TransactionInfo(
                txid=init,
                amount=1000 * random.random(),
                fee=100 * random.random(),
                confirmed=True if random.random() > 0.5 else False,
                block_height=init * 10 + 1,
            )
        )
        init += 1
    return txs


class ViewTransactionsMenu:

    def __init__(
        self, app_ctx: ApplicationContext, tx_service: TxService, wm: WalletManager
    ):
        self.app_ctx = app_ctx
        self.tx_service = tx_service
        self.wm = wm

    def show(self):
        t = self.app_ctx.get_terminal()

        def print_dummy():
            print("No transactions found")
            txs = dummy_data()
            table = PrettyTable()
            table.field_names = [
                "Transaction ID",
                "Amount",
                "Fee",
                "Confirmed",
                "Block Height",
            ]
            for tinfo in txs:
                table.add_row(
                    [
                        tinfo.txid,
                        tinfo.amount,
                        tinfo.fee,
                        tinfo.confirmed,
                        tinfo.block_height,
                    ]
                )
            print(table)

        with t.fullscreen():
            print(t.clear())
            if not self.wm.has_wallet():
                logging.error("No wallet found")
                press_any_key_to_return(t, UIStrings.to_menu(UIStrings.MAIN_MENU))
                return
            txs = self.wm.get_prvkey().get_transactions()
            print(t.reverse_bold("Your Bitcoin Transactions"))
            if len(txs) == 0:
                print_dummy()
            else:
                self.print_txs(txs)
            with t.location(0, t.height - 1):
                print(
                    t.bold_reverse(
                        "Press E to export transactions to CSV; press any other key to go back"
                    )
                )
            key = get_keypress(t)
            if not key:
                logging.warn("Logging out due to inactivity")
                on_shutdown(t)
            elif key.lower() == "e":
                self.export_txs(txs)
            else:
                return

    def print_txs(self, txs):
        table = PrettyTable()
        table.field_names = [
            "Transaction ID",
            "Amount",
            "Fee",
            "Confirmed",
            "Block Height",
        ]
        for tx in txs:
            tinfo = self.tx_service.get_tx(tx)
            table.add_row(
                [
                    tinfo.txid,
                    tinfo.amount,
                    tinfo.fee,
                    tinfo.confirmed,
                    tinfo.block_height,
                ]
            )
        print(table)

    def export_txs(self, txs):
        logging.info("Exporting transactions to file...")
        if len(txs) == 0:
            logging.error("No transactions found to export")
        else:
            with open("transactions.csv", "w") as f:
                f.write("Transaction ID,Amount,Fee,Confirmed,Block Height\n")
                for tinfo in txs:
                    f.write(
                        f"{tinfo.txid},{tinfo.amount},{tinfo.fee},{tinfo.confirmed},{tinfo.block_height}\n"
                    )
            print("Transactions exported successfully!")
