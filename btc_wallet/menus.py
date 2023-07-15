from argparse import Namespace
from .wallet_mgr import WalletManager
from .contact_mgr import ContactManager
from .user_service import UserService
from .tx_service import TxService
from .contact import Contact
from .util import btc_addr_is_valid, Modes, sats_to_btc, SATS_PER_BTC
import subprocess
import qrcode
from shutil import which
from prettytable import PrettyTable
import getpass
from blessings import Terminal # TODO

MENU_ERR_MSG = 'Invalid input - try again'

def start(args: Namespace):
  print(f"BTC Wallet app starting in {args.mode.value} mode...")
  global us
  us = UserService()
  if login():
    print("Password confirmed")
    # init wallet
    global wm, cm, txservice
    wm = WalletManager(args.mode)
    cm = ContactManager(args.mode)
    txservice = TxService(args.mode)
    main_menu(args.mode)
  else:
    quit()

def login():
  tries = 3
  while tries >= 0:
    pw = getpass.getpass()
    if us.validate_password(pw):
      return True
    else:
      print(f"ERROR: incorrect password. {tries} more tries remaining")
      tries -= 1
  return False

def main_menu(mode):
  choice = None
  while True:
    print("""
**********************
      MAIN MENU
**********************
1. View / manage bitcoin wallet
2. View / manage contact list
3. View bitcoin transactions
4. Send bitcoin
5. Change app password
6. Quit
""")
    try:
      choice = int(input("Choice: "))
      print()
    except ValueError:
      print(MENU_ERR_MSG)
      continue
    if choice < 1 or choice > 6:
      print("Error: Select an option...")
      continue
    if choice == 1:
      wallet_menu()
    elif choice == 2:
      contact_menu(mode)
    elif choice == 3:
      txs = wm.get_prvkey().get_transactions()
      print_txs(txs)
    elif choice == 4:
      tx_send_menu()
    elif choice == 5:
      print(f"Your current password is: {us.get_pw_from_file()}")
      newpw = input(f"Enter a new password: \n")
      us.save_pw(newpw)
      print(f"New password saved: {newpw}")
    elif choice == 6:
      break

def print_txs(txs):
  table = PrettyTable()
  table.field_names = ["Transaction ID", "Amount", "Fee", "Confirmed", "Block Height"]
  for tx in txs:
    tinfo = txservice.get_tx(tx)
    table.add_row([tinfo.txid, tinfo.amount, tinfo.fee, tinfo.confirmed, tinfo.block_height])
  print(table)

def wallet_menu():
  while True:
    print("""
**********************
     WALLET MENU
**********************
Choose an option:
1. Show bitcoin address
2. Recover bitcoin wallet
3. Generate new wallet
4. Back to main menu
    """)
    choice = None
    try:
      choice = int(input())
    except ValueError:
      print(MENU_ERR_MSG)
      continue
    if choice == 1:
      addr = wm.get_addr()
      print(addr)
      show_qr(addr)
      bal = int(wm.get_bal())
      if bal < (SATS_PER_BTC / 1000): # display as sats if < 0.001 btc
        print(f"Balance: {bal} sats")
      else: # display as btc if > 0.001 btc
        print(f"Balance: {sats_to_btc(bal):,.8f} btc")
    elif choice == 2:
      print("Enter your 12 or 24 words:")
      words = input()
      passphr = input("Enter your passphrase (if there is none, leave blank):")
      wm.recover(words,passphr)
    elif choice == 3:
      wm.generate()
    elif choice == 4:
      break

def contact_menu(mode):
  while True:
    print("""
**********************
    CONTACT MENU
**********************
1. View Contact List
2. Add new contact
3. Get individual contact
4. Back to main menu
""")
    choice = None
    try:
      choice = int(input())
    except ValueError:
      print(MENU_ERR_MSG)
      continue
    if choice == 1:
      cm.view_list()
    elif choice == 2:
      print("Enter new contact's name:")
      name = input()
      print("Enter new contact's BTC address:")
      addr = input()
      if (btc_addr_is_valid(addr, mode)):
        newid = cm.contacts[-1].id + 1
        cm.persist_new_contact(Contact(newid, name, addr))
        print(f'Contact added: {cm}')
      else:
        print('Invalid address - contact not added. Try again')
    elif choice == 3:
      contact_id = int(input('Enter the contact ID number to retrieve: '))
      contact = cm.get_contact(contact_id)
      if contact is None:
        print('Contact not found. Enter a valid contact ID')
      else:
        print(f"Name: {contact.name}")
        print(f"Bitcoin address (text): {contact.addr}")
        print("Bitcoin address (QR code):")
        show_qr(contact.addr)
    elif choice == 4:
      break

def show_qr(addr):
  # Display in console if 'qr' command installed, otherwise open file viewer
  if which('qr') is not None:
    subprocess.call(['qr', addr])
  else:
    qrcode.make(addr).show()

def tx_send_menu():
  choice = None
  print("Pick a contact to send a transaction to")
  cm.view_list()
  contact_id = int(input())
  to_addr = cm.get_contact(contact_id).addr
  print("How much BTC would you like to send?")
  bal = wm.get_bal()
  print(f"Available balance: {bal} sats")
  amount = int(input())
  print(f"""Transaction Summary:
  AMOUNT = {amount} satoshis
  TO = {to_addr}
  """)
  yn = input('Are you sure you want to send this transaction? (y/n) ')
  if yn == 'y':
    txid = wm.get_prvkey().send([(to_addr,amount, 'satoshi')])
    print(f"Transaction completed - TXID = {txid}")