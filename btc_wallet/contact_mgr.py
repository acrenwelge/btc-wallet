from os.path import expanduser
import csv
from btc_wallet.util import Modes
from .contact import Contact

class ContactManager:
  def __init__(self, mode: Modes) -> None:
    self.contacts = []
    self.filepath = "~/.wallet/"
    if mode == Modes.PROD:
      self.filepath += "contacts.csv"
    elif mode == Modes.TEST:
      self.filepath += "testcontacts.csv"
    try:
      with open(expanduser(self.filepath)) as f:
        reader = csv.reader(f)
        for row in reader:
          contact = Contact(row[0],row[1])
          self.contacts.append(contact)
    except FileNotFoundError:
      print("No contacts found")

  def view_list(self):
    if len(self.contacts) == 0:
      print("No contacts to list")
    idx = 0
    for contact in self.contacts:
      print(str(idx) + ') ' + contact.name)
      print(contact.addr)
      idx += 1

  def add_contact(self, new_contact):
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
    return self.contacts[id-1]