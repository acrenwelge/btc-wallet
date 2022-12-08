import mng_wallet
import mng_contact
import send_tx
from wallet_mgr import WalletManager

def start():
  print("BTC Wallet app starting...")
  if login():
    print("Password confirmed")
    # init wallet
    wallet_mgr = WalletManager()
    menu(wallet_mgr)
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

def menu(wallet_mgr):
  choice = None
  while True:
    print("Choose an option:")
    print("1. Manage/view your bitcoin wallet")
    print("2. View your contact list")
    print("3. Send transaction")
    print("4. Quit")
    choice = int(input())
    if choice >= 1 and choice <= 4:
      break
    else:
      print("Error: Select an option...")
  if choice == 1:
    mng_wallet.menu(wallet_mgr)
  elif choice == 2:
    mng_contact.menu(wallet_mgr)
  elif choice == 3:
    send_tx.menu(wallet_mgr)

if __name__ == "__main__":
  start()