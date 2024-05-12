import logging

from blessed import Terminal

from btc_wallet.contact import Contact
from btc_wallet.contact_mgr import ContactManager
from btc_wallet.menus.generic import generic_menu
from btc_wallet.menus.wallet import WalletMenu
from btc_wallet.util import (
    Modes,
    UIStrings,
    btc_addr_is_valid,
    get_user_input,
    press_any_key_to_return,
)


class ContactMenu:
    def __init__(self, t: Terminal, cm: ContactManager, mode: Modes):
        self.t = t
        self.cm = cm
        self.mode = mode

    def show_contacts(self):
        with self.t.fullscreen():
            print(self.t.clear())
            table = self.cm.get_list_as_table()
            if table is None:
                print("No contacts found")
            else:
                print(table)
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def add_contact_menu(self):
        with self.t.fullscreen():
            name = get_user_input(self.t, 1, "Enter new contact's name:")
            addr = get_user_input(self.t, 3, "Enter new contact's BTC address:")
            if btc_addr_is_valid(addr, self.mode):
                newid = self.cm.contacts[-1].id + 1
                self.cm.persist_new_contact(Contact(newid, name, addr))
                logging.info(f"Contact added: {self.cm}")
            else:
                logging.warn("Invalid address - contact not added. Try again")
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def get_contact_menu(self):
        with self.t.fullscreen():
            contact_id = int(
                get_user_input(self.t, 1, "Enter the contact ID number to retrieve: ")
            )
            contact = self.cm.get_contact(contact_id)
            with self.t.location(0, 4):
                if contact is None:
                    logging.warn("Contact not found. Enter a valid contact ID")
                else:
                    print(f"Name: {contact.name}")
                    print(f"Bitcoin address (text): {contact.addr}")
                    print("Bitcoin address (QR code):")
                    WalletMenu.show_qr(contact.addr)
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def edit_contact_menu(self):
        with self.t.fullscreen():
            contact_id_to_edit = int(
                get_user_input(self.t, 1, "Enter the contact ID number to edit: ")
            )
            contact = self.cm.get_contact(contact_id_to_edit)
            with self.t.location(0, 4):
                if contact is None:
                    logging.warn("Contact not found. Enter a valid contact ID")
                else:
                    print(f"Name: {contact.name}")
                    print(f"Bitcoin address (text): {contact.addr}")
                    new_name = get_user_input(
                        self.t,
                        7,
                        "Enter new name for contact (leave blank to keep the same):",
                    )
                    if new_name == "":
                        new_name = contact.name
                    new_addr = get_user_input(
                        self.t,
                        9,
                        "Enter new BTC address for contact (leave blank to keep the same):",
                    )
                    if new_addr == "":
                        new_addr = contact.addr
                    if btc_addr_is_valid(new_addr, self.mode):
                        confirm = get_user_input(
                            self.t,
                            11,
                            f"Confirm changes: {new_name} - {new_addr} (y/n)",
                        )
                        if confirm == "y":
                            self.cm.update_contact(
                                Contact(contact_id_to_edit, new_name, new_addr)
                            )
                            logging.info(f"Contact updated: {self.cm}")
                        else:
                            logging.warn("Contact not updated")
                    else:
                        print(self.t.clear())
                        logging.warn("Invalid address - contact not updated. Try again")
                press_any_key_to_return(
                    self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU)
                )

    def delete_contact_menu(self):
        with self.t.fullscreen():
            contact_id_to_delete = int(
                get_user_input(self.t, 1, "Enter the contact ID number to delete:")
            )
            yn = get_user_input(
                self.t,
                3,
                f"Are you sure you want to delete contact #{contact_id_to_delete}? (y/n)",
            )
            if yn != "y":
                logging.info(f"Contact #{contact_id_to_delete} not deleted")
                print(f"Contact #{contact_id_to_delete} not deleted")
                press_any_key_to_return(
                    self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU)
                )
                return
            completed = self.cm.delete_contact(contact_id_to_delete)
            print(self.t.clear())
            if completed:
                logging.info(f"Contact #{contact_id_to_delete} deleted successfully")
                print(f"Contact #{contact_id_to_delete} deleted successfully")
            else:
                logging.warn(
                    f"Contact #{contact_id_to_delete} not found - nothing deleted"
                )
                print(f"Contact #{contact_id_to_delete} not found - nothing deleted")
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.CONTACT_MENU))

    def show(self) -> None:

        menu_options = [
            ("View contact list", self.show_contacts),
            ("Add new contact", self.add_contact_menu),
            ("Get individual contact", self.get_contact_menu),
            ("Edit contact", self.edit_contact_menu),
            ("Delete contact", self.delete_contact_menu),
            ("Back to main menu", lambda: None),
        ]

        generic_menu(menu_options, UIStrings.CONTACT_MENU)
