from os.path import expanduser
import csv
from .contact import Contact

class ContactManager:
  def __init__(self) -> None:
    self.contacts = []
    try:
      with open(expanduser("~/.wallet/contacts.csv")) as f:
        reader = csv.reader(f)
        for row in reader:
          contact = Contact(row[0],row[1])
          self.contacts.append(contact)
    except FileNotFoundError:
      print("No contacts found")

  def view_list(self):
    if len(self.contacts) == 0:
      print("No contacts to list")
    for contact in self.contacts:
      print(contact.name)
      print(contact.addr)

  def add_contact(self, new_contact):
    self.contacts.append(new_contact)

  def get_contact(self, id: int) -> Contact:
    return self.contacts[id-1]

  