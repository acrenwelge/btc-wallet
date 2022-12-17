from wallet_mgr import WalletManager
from contact_mgr import ContactManager
from contact import Contact
import subprocess
import qrcode
from shutil import which
from util import *

def start():
  print("BTC Wallet app starting...")
  if login():
    print("Password confirmed")
    # init wallet
    global wm, cm
    wm = WalletManager()
    cm = ContactManager()
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
    choice = int(input())
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
    choice = int(input())
    if choice == 1:
      addr = wm.get_addr()
      print(addr)
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
    choice = int(input())
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
      # Display in console if 'qr' command installed, otherwise open file viewer
      if which('qr') is not None:
        subprocess.call(['qr', contact.addr])
      else:
        qrcode.make(contact.addr).show()
    elif choice == 4:
      break
  main_menu()

def tx_menu():
  print("1. Send a transaction")

if __name__ == "__main__":
  start()