import getpass
import logging
import subprocess
from argparse import Namespace
from shutil import which
from typing import Callable, List, Tuple

import qrcode
from bit.exceptions import InsufficientFunds
from blessed import Terminal
from prettytable import PrettyTable

from .contact import Contact
from .contact_mgr import ContactManager
from .tx_service import TxService
from .user_service import UserService
from .util import (
    SATS_PER_BTC,
    Modes,
    btc_addr_is_valid,
    get_keypress,
    get_user_input,
    press_any_key_to_return,
    sats_to_btc,
)
from .wallet_mgr import WalletAlreadyExistsError, WalletManager

t = Terminal()


class UIStrings:
    MAIN_MENU = "MAIN MENU"
    WALLET_MENU = "WALLET MENU"
    CONTACT_MENU = "CONTACT MENU"
    TX_SEND_MENU = "SEND BITCOIN"

    @classmethod
    def to_menu(cls, menu_name: str):
        return f"to the {menu_name.lower()}"


def start(args: Namespace):
    global mode, user_service
    mode = args.mode
    logging.info(f"Starting app in {mode.value} mode...")
    user_service = UserService()
    global wm, cm, tx_service
    wm = WalletManager(mode)
    cm = ContactManager(mode)
    tx_service = TxService(mode)
    if not wm.seedfile_exists():
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
        main_menu()
        quit()
    tries = 3
    while tries > 0:
        pw = getpass.getpass()
        success = wm.load_seed(pw)
        if success:
            logging.info("Wallet loaded successfully")
            main_menu()
            quit()
        else:
            tries -= 1
            logging.error(
                f"Incorrect password - wallet could not be loaded. {tries} more chances"
            )
    logging.info("Maximum password attempts reached - quitting")
    quit()


class TransactionInfo:
    def __init__(self, txid, amount, fee, confirmed, block_height):
        self.txid = txid
        self.amount = amount
        self.fee = fee
        self.confirmed = confirmed
        self.block_height = block_height

    def __str__(self):
        return f"TXID: {self.txid}, Amount: {self.amount}, Fee: {self.fee}, Confirmed: {self.confirmed}, Block Height: {self.block_height}"


def main_menu():
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

    def view_txs():
        txs = wm.get_prvkey().get_transactions()
        with t.fullscreen():
            print(t.clear())
            print(t.reverse_bold("Your Bitcoin Transactions"))
            if len(txs) == 0:
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
            else:
                print_txs(txs)
            with t.location(0, t.height - 1):
                print(
                    t.bold_reverse(
                        "Press E to export transactions to CSV; press any other key to go back"
                    )
                )
            key = get_keypress(t)
            if not key:
                logging.warn("Logging out due to inactivity")
                quit()
            elif key.lower() == "e":
                export_txs(txs)
            else:
                return

    def print_txs(txs):
        table = PrettyTable()
        table.field_names = [
            "Transaction ID",
            "Amount",
            "Fee",
            "Confirmed",
            "Block Height",
        ]
        for tx in txs:
            tinfo = tx_service.get_tx(tx)
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

    def export_txs(txs):
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

    menu_options = [
        ("Bitcoin wallet", wallet_menu),
        ("Manage contact list", lambda: contact_menu(mode)),
        ("View bitcoin transactions", view_txs),
        ("Send bitcoin", tx_send_menu),
        ("Quit", lambda: None),
    ]
    generic_menu(menu_options, UIStrings.MAIN_MENU)


def generic_menu(menu_options: List[Tuple[str, Callable]], menu_name) -> int:
    """
    Displays a generic menu with the given options and menu name.
    User selects an option and the corresponding function is called.
    """
    selected_option_index = 0

    with t.fullscreen(), t.cbreak(), t.hidden_cursor():
        while True:
            print(t.clear)
            print("*" * t.width)
            print(
                t.bold(
                    t.black(t.on_white(f"{menu_name}   ({mode.value.upper()} MODE)"))
                ).center(t.width)
            )  # TODO: centering is off...
            print("*" * t.width)
            if mode == Modes.TEST:
                print(
                    t.red(
                        "WARNING: You are in TESTNET mode. This mode is only for testing and using test bitcoin. Do not enter real bitcoin addresses or send real bitcoin!"
                    )
                )
            elif mode == Modes.PROD:
                print(
                    t.green(
                        "WARNING: You are in MAINNET mode. Do NOT enter testnet addresses. Be careful with real bitcoin!"
                    )
                )
            for i, option in enumerate(menu_options):
                if i == selected_option_index:
                    print(t.bold_reverse(option[0]))  # Highlight the selected option
                else:
                    print(option[0])

            with t.location(0, t.height - 1):
                print("Use arrow keys to navigate, ENTER to select, and Q to quit.")

            key = get_keypress(t)

            if key.name == "KEY_UP":
                selected_option_index = max(0, selected_option_index - 1)
            elif key.name == "KEY_DOWN":
                selected_option_index = min(
                    len(menu_options) - 1, selected_option_index + 1
                )
            elif key.name == "KEY_ENTER":
                # execute the function corresponding to the selected option
                func = menu_options[selected_option_index][1]
                logging.info(menu_options[selected_option_index][0])
                func()
                if selected_option_index == len(menu_options) - 1:
                    break  # Exit the menu loop if the last option is selected
            elif key.lower() == "q":
                quit()
            elif not key:  # timeout
                logging.warn("Logging out due to inactivity")
                quit()


def wallet_menu():
    def show_addr():
        with t.fullscreen():
            copied = False
            while True:
                print(t.clear)
                try:
                    addr = wm.get_addr()
                except ValueError:
                    logging.error("No wallet found")
                    press_any_key_to_return(t, UIStrings.to_menu(UIStrings.WALLET_MENU))
                    return
                print(addr)
                show_qr(addr)
                bal = wm.get_bal()
                if bal < (SATS_PER_BTC / 1000):  # display as sats if < 0.001 btc
                    print(f"Balance: {bal} sats")
                else:  # display as btc if > 0.001 btc
                    print(f"Balance: {sats_to_btc(bal):,.8f} btc")
                with t.location(0, t.height - 2):
                    if copied:
                        print(t.bold_reverse("Address copied to clipboard!"))
                    print(
                        "Press C to copy the address; ENTER to return to wallet menu."
                    )
                key = get_keypress(t)
                if key.lower() == "c":
                    import pyperclip

                    pyperclip.copy(addr)
                    copied = True
                else:
                    break

    def recover_wallet():
        with t.fullscreen(), t.hidden_cursor():
            words = get_user_input(t, 1, "Enter your 12 or 24 word seed phrase:")
            if len(words.split()) not in [12, 24]:
                with t.location(0, 7):
                    logging.error(
                        t.bold_reverse(
                            "Invalid number of words - must be 12 or 24 words"
                        )
                    )
                press_any_key_to_return(t, "to the wallet menu")
                return
            passphr = get_user_input(
                t, 4, "Enter your passphrase (if there is none, leave blank):"
            )
            try:
                wm.recover(words, passphr)
            except WalletAlreadyExistsError:
                with t.location(0, 7):
                    logging.error(
                        t.bold_reverse(
                            "Wallet already exists, cannot recover new wallet"
                        )
                    )
                press_any_key_to_return(t, UIStrings.to_menu(UIStrings.WALLET_MENU))

    def generate_wallet():
        with t.fullscreen():
            print(t.clear())
            if wm.has_wallet():
                with t.location(0, 7):
                    logging.error(
                        t.bold_reverse(
                            "Wallet already exists, cannot generate new wallet"
                        )
                    )
                press_any_key_to_return(t, "to the wallet menu")
                return
            passphrase = get_user_input(
                t,
                1,
                "Enter a passphrase for your new wallet (make it unique but memorable!). This is optional - if you do not want to set a passphrase, leave blank",
            )
            encryption_password = get_user_input(
                t,
                3,
                "Enter a password to encrypt your wallet file. This is optional - if you do not want to encrypt your wallet file, leave blank. Remember this password, as you will need it to access your wallet.",
            )
            with t.location(0, 7):
                print("Wallet passphrase: " + passphrase)
                print("Encryption password: " + encryption_password)
            yn = get_user_input(
                t, 10, "Are you sure you want to generate a new wallet? (y/n)"
            )
            if yn == "y":
                words, bin_seed, entropy = wm.generate(passphrase, encryption_password)
                logging.info("Wallet generated")
                print(
                    """
      *******************************************************************************
      Your wallet has been generated!
      INSTRUCTIONS: WRITE DOWN THE FOLLOWING WORDS TO BACKUP YOUR WALLET AND STORE IN A SAFE AND SECURE OFFLINE LOCATION.
      THIS BACKUP SEED PHRASE WILL BE USED TO RECOVER YOUR WALLET IF YOU LOSE ACCESS TO THIS DEVICE.
      THIS BACKUP PHRASE WILL NOT BE SAVED ANYWHERE ON THIS DEVICE. FAILURE TO SECURE THIS BACKUP SEED PHRASE MAY CAUSE YOU TO LOSE YOUR BITCOIN.
      !!DO NOT FORGET THESE!!
      *******************************************************************************
      """
                )
                print("*" * 20)
                print(words)
                print("*" * 20)
                print(f"\nThe binary seed from the mnemonic is: {bin_seed.hex()}")
                print(f"Entropy = {entropy}\n")
            else:
                logging.warn("Wallet generation cancelled")
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.WALLET_MENU))

    menu_options = [
        ("Show bitcoin address", show_addr),
        ("Recover bitcoin wallet", recover_wallet),
        ("Generate new wallet", generate_wallet),
        ("Back to main menu", lambda: None),
    ]
    generic_menu(menu_options, UIStrings.WALLET_MENU)


def contact_menu(mode):

    def show_contacts():
        with t.fullscreen():
            print(t.clear())
            table = cm.get_list()
            if table is None:
                print("No contacts found")
            else:
                print(table)
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def add_contact():
        with t.fullscreen():
            name = get_user_input(t, 1, "Enter new contact's name:")
            addr = get_user_input(t, 3, "Enter new contact's BTC address:")
            if btc_addr_is_valid(addr, mode):
                newid = cm.contacts[-1].id + 1
                cm.persist_new_contact(Contact(newid, name, addr))
                logging.info(f"Contact added: {cm}")
            else:
                logging.warn("Invalid address - contact not added. Try again")
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def get_contact():
        with t.fullscreen():
            contact_id = int(
                get_user_input(t, 1, "Enter the contact ID number to retrieve: ")
            )
            contact = cm.get_contact(contact_id)
            with t.location(0, 4):
                if contact is None:
                    logging.warn("Contact not found. Enter a valid contact ID")
                else:
                    print(f"Name: {contact.name}")
                    print(f"Bitcoin address (text): {contact.addr}")
                    print("Bitcoin address (QR code):")
                    show_qr(contact.addr)
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def edit_contact():
        with t.fullscreen():
            contact_id_to_edit = int(
                get_user_input(t, 1, "Enter the contact ID number to edit: ")
            )
            contact = cm.get_contact(contact_id_to_edit)
            with t.location(0, 4):
                if contact is None:
                    logging.warn("Contact not found. Enter a valid contact ID")
                else:
                    print(f"Name: {contact.name}")
                    print(f"Bitcoin address (text): {contact.addr}")
                    new_name = get_user_input(
                        t,
                        7,
                        "Enter new name for contact (leave blank to keep the same):",
                    )
                    if new_name == "":
                        new_name = contact.name
                    new_addr = get_user_input(
                        t,
                        9,
                        "Enter new BTC address for contact (leave blank to keep the same):",
                    )
                    if new_addr == "":
                        new_addr = contact.addr
                    if btc_addr_is_valid(new_addr, mode):
                        confirm = get_user_input(
                            t, 11, f"Confirm changes: {new_name} - {new_addr} (y/n)"
                        )
                        if confirm == "y":
                            cm.update_contact(
                                Contact(contact_id_to_edit, new_name, new_addr)
                            )
                            logging.info(f"Contact updated: {cm}")
                        else:
                            logging.warn("Contact not updated")
                    else:
                        print(t.clear())
                        logging.warn("Invalid address - contact not updated. Try again")
                press_any_key_to_return(t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def delete_contact():
        with t.fullscreen():
            contact_id_to_delete = int(
                get_user_input(t, 1, "Enter the contact ID number to delete:")
            )
            completed = cm.delete_contact(contact_id_to_delete)
            if completed:
                logging.info(f"Contact #{contact_id_to_delete} deleted successfully")
                print(f"Contact #{contact_id_to_delete} deleted successfully")
            else:
                logging.warn(
                    f"Contact #{contact_id_to_delete} not found - nothing deleted"
                )
                print(f"Contact #{contact_id_to_delete} not found - nothing deleted")
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    menu_options = [
        ("View contact list", show_contacts),
        ("Add new contact", add_contact),
        ("Get individual contact", get_contact),
        ("Edit contact", edit_contact),
        ("Delete contact", delete_contact),
        ("Back to main menu", lambda: None),
    ]

    generic_menu(menu_options, UIStrings.CONTACT_MENU)


def show_qr(addr):
    # Display in console if 'qr' command installed, otherwise open file viewer
    if which("qr") is not None:
        subprocess.call(["qr", addr])
    else:
        qrcode.make(addr).show()


def tx_send_menu():
    with t.fullscreen():
        print("Pick a contact to send a transaction to")
        table = cm.get_list()
        if table is None:
            print(t.bold_reverse("No contacts found"))
            press_any_key_to_return(t, UIStrings.to_menu(UIStrings.MAIN_MENU))
            return
        contact_id = int(get_user_input(t, 1, "Enter the contact ID number: "))
        contact = cm.get_contact(contact_id)
        to_addr = contact.addr
        bal = str(wm.get_bal())
        print(f"Your available balance: {bal} sats")
        amount = int(
            get_user_input(t, 4, "How much BTC would you like to send (in sats)?")
        )
        print(
            f"""Transaction Summary:
  TO (NAME) = {contact.name}
  TO (ADDRESS) = {to_addr}
  AMOUNT = {amount} satoshis
  """
        )
        yn = get_user_input(
            t, 11, "Are you sure you want to send this transaction? (y/n) "
        )
        if yn == "y":
            try:
                txid = wm.get_prvkey().send([(to_addr, amount, "satoshi")])
                logging.info(f"Transaction completed - TXID = {txid}")
            except InsufficientFunds:
                logging.error("Insufficient funds - transaction not sent")
        else:
            logging.warn("Transaction cancelled")
        press_any_key_to_return(t, UIStrings.to_menu(UIStrings.MAIN_MENU))
