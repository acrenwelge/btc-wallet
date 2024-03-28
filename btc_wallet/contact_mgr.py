import csv
import logging
from os.path import expanduser
from typing import List

from prettytable import PrettyTable

from btc_wallet.contact import Contact
from btc_wallet.util import Modes


class ContactManager:
    contacts: List[Contact]
    filepath: str

    def __init__(self, mode: Modes) -> None:
        self.contacts = []
        self.filepath = "~/.wallet/"
        if mode == Modes.PROD:
            self.filepath += "contacts.csv"
        elif mode == Modes.TEST:
            self.filepath += "testcontacts.csv"
        self.load_contacts_from_file()

    def load_contacts_from_file(self):
        self.contacts = []
        try:
            with open(expanduser(self.filepath)) as f:
                reader = csv.reader(f)
                for row in reader:
                    contact = Contact(int(row[0]), row[1], row[2])
                    self.contacts.append(contact)
            self.contacts.sort(key=lambda x: x.id)
        except FileNotFoundError:
            logging.error("Contact file not found")

    def view_list(self):
        if len(self.contacts) == 0:
            logging.error("No contacts to list")
        table = PrettyTable()
        table.field_names = ["#", "Name", "BTC Address"]
        for contact in self.contacts:
            table.add_row([contact.id, contact.name, contact.addr])
        print(table)

    def add_contact(self, new_contact: Contact):
        self.contacts.append(new_contact)

    def update_contact(self, updated_contact: Contact):
        for contact in self.contacts:
            if contact.id == updated_contact.id:
                contact.name = updated_contact.name
                contact.addr = updated_contact.addr
        self.save_contacts_to_file()
        logging.debug(f"Contact updated: {contact}")

    def save_contacts_to_file(self):
        try:
            with open(expanduser(self.filepath), "w") as f:
                writer = csv.writer(f)
                for contact in self.contacts:
                    writer.writerow([contact.id, contact.name, contact.addr])
        except IOError:
            logging.error("Contacts not saved to file - something went wrong")

    def persist_new_contact(self, new_contact: Contact):
        try:
            with open(expanduser(self.filepath), "a") as f:
                writer = csv.writer(f)
                writer.writerow([new_contact.id, new_contact.name, new_contact.addr])
        except IOError:
            logging.error("Contact not saved to file - something went wrong")
        self.load_contacts_from_file()

    def delete_contact(self, id: int):
        for contact in self.contacts:
            if contact.id == id:
                self.contacts.remove(contact)
                self.save_contacts_to_file()
                logging.info(f"Contact deleted: {contact}")
                return
        logging.warn(f"Contact not found: {id}")

    def get_contact(self, id: int) -> Contact:
        for contact in self.contacts:
            if contact.id == id:
                logging.debug(f"Contact found: {contact}")
                return contact
        logging.warn(f"Contact not found: {id}")
