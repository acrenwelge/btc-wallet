import logging

from bit.exceptions import InsufficientFunds
from bit.network import get_fee
from blessed import Terminal

from btc_wallet.application_context import ApplicationContext
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.user_settings import FeeTypes
from btc_wallet.util import UIStrings, get_user_input, press_any_key_to_return
from btc_wallet.wallet_mgr import WalletManager


class SendTransactionsMenu:

    def __init__(self, t: Terminal, cm: ContactManager, wm: WalletManager):
        self.t = t
        self.cm = cm
        self.wm = wm

    def show(self):
        with self.t.fullscreen():
            contact = self.pick_contact()
            if contact is None:
                logging.error("Contact not found - please enter a valid contact ID")
                press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.MAIN_MENU))
                return
            bal = self.wm.get_bal_sats()
            print(f"Your available balance: {str(bal)} sats")
            amount = int(
                get_user_input(
                    self.t, 4, "How much BTC would you like to send (in sats)?"
                )
            )
            if amount > bal:
                logging.error("Insufficient funds - transaction not sent")
                press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.MAIN_MENU))
                return
            self.confirm_transaction(contact, amount)
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.MAIN_MENU))

    def pick_contact(self):
        print("Pick a contact to send a transaction to")
        table = self.cm.get_list_as_table()
        if table is None:
            print(self.t.bold_reverse("No contacts found"))
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.MAIN_MENU))
            return
        else:
            print(table)
        try:
            contact_id = int(
                get_user_input(
                    self.t, self.t.height - 1, "Enter the contact ID number: "
                )
            )
        except ValueError:
            logging.error("Invalid contact ID - must be an integer")
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.MAIN_MENU))
            return
        return self.cm.get_contact(contact_id)

    def confirm_transaction(self, contact, amount):
        fee_type = ApplicationContext.get_user_settings().fee_type
        fast_fee = True if fee_type == FeeTypes.priority.value else False
        est_fee = get_fee(fast=fast_fee)
        print(
            f"""Transaction Summary:
        TO (NAME) = {contact.name}
        TO (ADDRESS) = {contact.to_addr}
        AMOUNT = {amount} satoshis
        ESTIMATED FEE = {est_fee} satoshis
        """
        )
        yn = get_user_input(
            self.t, 11, "Are you sure you want to send this transaction? (y/n) "
        )
        if yn == "y":
            try:
                txid = self.wm.get_prvkey().send(
                    [(contact.to_addr, amount, "satoshi")], fee=est_fee
                )
                logging.info(f"Transaction completed - TXID = {txid}")
            except InsufficientFunds:
                logging.error("Insufficient funds - transaction not sent")
        else:
            logging.warn("Transaction cancelled")
