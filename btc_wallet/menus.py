from argparse import Namespace
from .wallet_mgr import WalletManager
from .contact_mgr import ContactManager
from .contact import Contact
from .util import btc_addr_is_valid
import subprocess
import qrcode
from shutil import which

def start(args: Namespace):
  print(f"BTC Wallet app starting in {args.mode.value} mode...")
  if login():
    print("Password confirmed")
    # init wallet
    global wm, cm
    wm = WalletManager(args.mode)
    cm = ContactManager(args.mode)
    main_menu()
  else:
    quit()

def login():
  tries = 3
  while tries > 0:
    print("Login with your password:")
    pw = input()
    if pw != "btc":
      print(f"ERROR: incorrect password. {tries} more tries remaining")
      tries -= 1
    else:
      return True
  return False

def main_menu():
  choice = None
  while True:
    print("Choose an option:")
    print("1. View / manage bitcoin wallet")
    print("2. View / manage contact list")
    print("3. Send bitcoin transaction")
    print("4. Quit")
    try:
      choice = int(input())
    except ValueError:
      print('Invalid input - try again')
      continue
    if choice >= 1 and choice <= 4:
      break
    else:
      print("Error: Select an option...")
  if choice == 1:
    wallet_menu()
  elif choice == 2:
    contact_menu()
  elif choice == 3:
    tx_menu()

def wallet_menu():
  while True:
    print("Choose an option:")
    print("1. Show bitcoin address")
    print("2. Recover bitcoin wallet")
    print("3. Generate new wallet")
    print("4. Back to main menu")
    choice = None
    try:
      choice = int(input())
    except ValueError:
      print('Invalid input - try again')
      continue
    if choice == 1:
      addr = wm.get_addr()
      print(addr)
      show_qr(addr)
    elif choice == 2:
      print("Enter your 12 or 24 words:")
      words = input()
      passphr = input("Enter your passphrase (if there is none, leave blank):")
      wm.recover(words,passphr)
      print("Recovery complete")
    elif choice == 3:
      wm.generate()
    elif choice == 4:
      break
  main_menu()

def contact_menu():
  while True:
    print("1. View Contact List")
    print("2. Add new contact")
    print("3. Get individual contact")
    print("4. Back to main menu")
    choice = None
    try:
      choice = int(input())
    except ValueError:
      print('Invalid input - try again')
      continue
    if choice == 1:
      cm.view_list()
    elif choice == 2:
      print("Enter new contact's name:")
      name = input()
      print("Enter new contact's BTC address:")
      addr = input()
      if (btc_addr_is_valid(addr)):
        cm.add_contact(Contact(name, addr))
        print(f'Contact added: {cm}')
      else:
        print('Invalid address - contact not added. Try again')
    elif choice == 3:
      print('Enter the contact ID number to retrieve:')
      contact_id = int(input())
      contact = cm.get_contact(contact_id)
      print(f"Name: {contact.name}")
      print(f"Bitcoin address (text): {contact.addr}")
      print("Bitcoin address (QR code):")
      show_qr(contact.addr)
    elif choice == 4:
      break
  main_menu()

def show_qr(addr):
  # Display in console if 'qr' command installed, otherwise open file viewer
  if which('qr') is not None:
    subprocess.call(['qr', addr])
  else:
    qrcode.make(addr).show()

def tx_menu():
  print("1. Send a transaction")
  print("2. View past transactions")
  choice = None
  try:
    choice = int(input())
  except ValueError:
    print("Invalid input - try again")
  if choice == 1:
    print("Pick a contact to send a transaction to")
    cm.view_list()
    contact_id = int(input())
    to_addr = cm.get_contact(contact_id).addr
    print("How much BTC would you like to send?")
    print(f"Available balance: X BTC") # TODO: implement
    # TODO: finish tx