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
    get_user_input,
    press_any_key_to_return,
    sats_to_btc,
)
from .wallet_mgr import WalletAlreadyExistsError, WalletManager

MENU_ERR_MSG = "Invalid input - try again"
t = Terminal()


def start(args: Namespace):
    global mode, user_service
    mode = args.mode
    logging.info(f"Starting app in {mode.value} mode...")
    user_service = UserService()
    if login():
        logging.info("Password confirmed")
        # init wallet
        global wm, cm, tx_service
        wm = WalletManager(mode)
        cm = ContactManager(mode)
        tx_service = TxService(mode)
        main_menu()
    else:
        logging.info("Password incorrect - quitting")
        quit()


def login():
    tries = 3
    while tries >= 0:
        pw = getpass.getpass()
        if user_service.validate_password(pw):
            return True
        else:
            logging.warn(f"ERROR: incorrect password. {tries} more tries remaining")
            tries -= 1
    return False


def main_menu():
    def view_txs():
        txs = wm.get_prvkey().get_transactions()
        print(t.clear())
        print_txs(txs)

    def change_pw():
        with t.fullscreen():
            print(f"Your current password is: {user_service.get_pw_from_file()}")
            newpw = input("Enter a new password: \n")
            user_service.save_pw(newpw)
            logging.info("New password saved")
            print("Password changed successfully!")
            press_any_key_to_return(t, "to the main menu")

    menu_options = [
        ("Bitcoin wallet", wallet_menu),
        ("Manage contact list", lambda: contact_menu(mode)),
        ("View bitcoin transactions", view_txs),
        ("Send bitcoin", tx_send_menu),
        ("Change app password", change_pw),
        ("Quit", lambda: None),
    ]
    generic_menu(menu_options, "MAIN MENU")


"""
Displays a generic menu with the given options and menu name.
User selects an option and the corresponding function is called.
"""


def generic_menu(menu_options: List[Tuple[str, Callable]], menu_name) -> int:
    selected_option_index = 0

    with t.fullscreen(), t.cbreak(), t.hidden_cursor():
        while True:
            print(t.clear)
            print("*" * t.width)
            print(
                t.bold(
                    t.black(t.on_white(f"{menu_name}   ({mode.value.upper()} MODE)"))
                ).center(t.width)
            )  # centering is off...
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

            key = t.inkey()

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


def print_txs(txs):
    table = PrettyTable()
    table.field_names = ["Transaction ID", "Amount", "Fee", "Confirmed", "Block Height"]
    for tx in txs:
        tinfo = tx_service.get_tx(tx)
        table.add_row(
            [tinfo.txid, tinfo.amount, tinfo.fee, tinfo.confirmed, tinfo.block_height]
        )
    print(table)


def wallet_menu():
    def show_addr():
        with t.fullscreen():
            copied = False
            while True:
                print(t.clear)
                addr = wm.get_addr()
                print(addr)
                show_qr(addr)
                bal = int(wm.get_bal())
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
                key = t.inkey()
                if key.lower() == "c":
                    import pyperclip

                    pyperclip.copy(addr)
                    copied = True
                else:
                    break

    def recover_wallet():
        with t.fullscreen(), t.hidden_cursor():
            words = ""
            passphr = ""
            while True:
                with t.location(0, 1):
                    print("Enter your 12 or 24 word seed phrase:")
                    print(words)
                key = t.inkey()
                if key.isalnum() or key == " ":
                    words += key
                elif key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
                    words = words[:-1]
                elif key.name == "KEY_ENTER":
                    break
            while True:
                with t.location(0, 4):
                    print("Enter your passphrase (if there is none, leave blank):")
                    print(passphr)
                key = t.inkey()
                if key.isalnum() or key == " ":
                    passphr += key
                    print(passphr)
                elif key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
                    t.get_location()
                    passphr = passphr[:-1]
                    print(passphr)
                elif key.name == "KEY_ENTER":
                    break
            if len(words.split()) not in [12, 24]:
                with t.location(0, 7):
                    logging.error(
                        t.bold_reverse(
                            "Invalid number of words - must be 12 or 24 words"
                        )
                    )
                    print(t.bold_reverse("Hit any key to return to the menu"))
                    t.inkey()
                    return
            try:
                wm.recover(words, passphr)
            except WalletAlreadyExistsError:
                with t.location(0, 7):
                    logging.error(
                        t.bold_reverse(
                            "Wallet already exists, cannot recover new wallet"
                        )
                    )
                    print(t.bold_reverse("Hit any key to return to the menu"))
                    t.inkey()

    def generate_wallet():
        if wm.has_wallet():
            with t.location(0, 7):
                logging.error(
                    t.bold_reverse("Wallet already exists, cannot generate new wallet")
                )
                print(t.bold_reverse("Hit any key to return to the menu"))
                t.inkey()
                return
        wm.generate()

    menu_options = [
        ("Show bitcoin address", show_addr),
        ("Recover bitcoin wallet", recover_wallet),
        ("Generate new wallet", generate_wallet),
        ("Back to main menu", lambda: None),
    ]
    generic_menu(menu_options, "WALLET MENU")


def contact_menu(mode):
    return_str = "to the contact menu"

    def show_contacts():
        with t.fullscreen():
            print(t.clear())
            table = cm.get_list()
            if table is None:
                print("No contacts found")
            else:
                print(table)
            press_any_key_to_return(t, return_str)

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
            press_any_key_to_return(t, return_str)

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
            press_any_key_to_return(t, return_str)

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
                        logging.warn("Invalid address - contact not updated. Try again")
                press_any_key_to_return(t, return_str)

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

    menu_options = [
        ("View contact list", show_contacts),
        ("Add new contact", add_contact),
        ("Get individual contact", get_contact),
        ("Edit contact", edit_contact),
        ("Delete contact", delete_contact),
        ("Back to main menu", lambda: None),
    ]

    generic_menu(menu_options, "CONTACT MENU")


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
            press_any_key_to_return(t, "to the main menu")
            return
        contact_id = int(get_user_input(t, 1, "Enter the contact ID number: "))
        contact = cm.get_contact(contact_id)
        to_addr = contact.addr
        bal = wm.get_bal()
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
        press_any_key_to_return(t, "to the main menu")
