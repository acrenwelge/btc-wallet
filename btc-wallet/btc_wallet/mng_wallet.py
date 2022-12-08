import home
from wallet_mgr import WalletManager

def menu(wallet_mgr: WalletManager):
  while True:
    print("Choose an option:")
    print("1. Show bitcoin address")
    print("2. Recover bitcoin wallet")
    print("3. Generate new wallet")
    print("4. Back to main menu")
    choice = int(input())
    if choice == 1:
      addr = wallet_mgr.get_addr()
      print(addr)
    elif choice == 2:
      print("Enter your 12 or 24 words:")
      words = input()
      passphr = input("Enter your passphrase (if there is none, leave blank):")
      wallet_mgr.recover(words,passphr)
      print("Recovery complete")
    elif choice == 3:
      wallet_mgr.generate()
    elif choice == 4:
      break
  home.menu(wallet_mgr)