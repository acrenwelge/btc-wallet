from os.path import expanduser
import csv
from typing import List
from btc_wallet.util import Modes
from btc_wallet.contact import Contact
from prettytable import PrettyTable

class ContactManager:
  def __init__(self, mode: Modes) -> None:
    self.contacts: List[Contact] = []
    self.filepath = "~/.wallet/"
    if mode == Modes.PROD:
      self.filepath += "contacts.csv"
    elif mode == Modes.TEST:
      self.filepath += "testcontacts.csv"
    try:
      with open(expanduser(self.filepath)) as f:
        reader = csv.reader(f)
        for row in reader:
          contact = Contact(int(row[0]),row[1],row[2])
          self.contacts.append(contact)
    except FileNotFoundError:
      print("No contacts found")

  def view_list(self):
    if len(self.contacts) == 0:
      print("No contacts to list")
    idx = 0
    table = PrettyTable()
    table.field_names = ['#', 'Name', 'BTC Address']
    for contact in self.contacts:
      table.add_row([contact.id, contact.name, contact.addr])
      idx += 1
    print(table)

  def add_contact(self, new_contact: Contact):
    self.contacts.append(new_contact)

  def persist_new_contact(self, new_contact: Contact):
    try:
      with open(expanduser(self.filepath),'a') as f:
        writer = csv.writer(f)
        writer.writerow([new_contact.name, new_contact.addr])
        self.add_contact(new_contact)
    except IOError:
      print("Contact not saved - something went wrong")

  def get_contact(self, id: int) -> Contact:
    for contact in self.contacts:
      if contact.id == id:
        return contact