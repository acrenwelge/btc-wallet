import logging
import subprocess
from shutil import which

import qrcode
from babel.numbers import format_currency
from blessed import Terminal

from btc_wallet.application_context import ApplicationContext
from btc_wallet.menus.generic import generic_menu
from btc_wallet.wallet_mgr import WalletAlreadyExistsError, WalletManager

from ..price_service import get_btc_price
from ..util import (
    SATS_PER_BTC,
    UIStrings,
    get_keypress,
    get_user_input,
    press_any_key_to_return,
    sats_to_btc,
)


class WalletMenu:

    def __init__(self, t: Terminal, wm: WalletManager):
        self.t = t
        self.wm = wm

    def show_addr(self):
        with self.t.fullscreen():
            copied = False
            while True:
                print(self.t.clear)
                try:
                    addr = self.wm.get_addr()
                except ValueError:
                    logging.error("No wallet found")
                    press_any_key_to_return(
                        self.t, UIStrings.to_menu(UIStrings.WALLET_MENU)
                    )
                    return
                print(addr)
                self.show_qr(addr)
                bal = self.wm.get_bal()
                if bal < (SATS_PER_BTC / 1000):  # display as sats if < 0.001 btc
                    print(f"Balance: {bal} sats")
                else:  # display as btc if > 0.001 btc
                    print(f"Balance: {sats_to_btc(bal):,.8f} btc")
                price = get_btc_price(currency="usd")
                fiat_bal = sats_to_btc(bal) * price
                fiat_cur = ApplicationContext.get_user_settings().currency
                print(f"Current fiat balance: {format_currency(fiat_bal, fiat_cur)}")
                with self.t.location(0, self.t.height - 2):
                    if copied:
                        print(self.t.bold_reverse("Address copied to clipboard!"))
                    print(
                        "Press C to copy the address; ENTER to return to wallet menu."
                    )
                key = get_keypress(self.t)
                if key.lower() == "c":
                    import pyperclip

                    pyperclip.copy(addr)
                    copied = True
                else:
                    break

    @staticmethod
    def show_qr(addr):
        """Displays a QR code in console if 'qr' command installed, otherwise open file viewer"""
        if which("qr") is not None:
            subprocess.call(["qr", addr])
        else:
            qrcode.make(addr).show()

    def recover_wallet(self):
        with self.t.fullscreen(), self.t.hidden_cursor():
            words = get_user_input(
                self.t, 1, "Enter your 12, 18, or 24 word seed phrase:"
            )
            if len(words.split()) not in [12, 18, 24]:
                with self.t.location(0, 7):
                    logging.error(
                        self.t.bold_reverse(
                            "Invalid number of words - must be 12, 18, or 24 words"
                        )
                    )
                press_any_key_to_return(self.t, "to the wallet menu")
                return
            passphr = get_user_input(
                self.t,
                4,
                "Enter your BIP-39 passphrase for the wallet (if there is none, leave blank):",
            )
            encryption_pw = get_user_input(
                self.t,
                6,
                "(Optional) Enter an encryption password which will be used to encrypt your private key on this device. If you do not want to encrypt your private key, leave blank:",
            )
            try:
                self.wm.recover(words, passphr, encryption_pw)
            except WalletAlreadyExistsError:
                with self.t.location(0, 7):
                    logging.error(
                        self.t.bold_reverse(
                            "Wallet already exists, cannot recover new wallet"
                        )
                    )
                press_any_key_to_return(
                    self.t, UIStrings.to_menu(UIStrings.WALLET_MENU)
                )

    def generate_wallet(self):
        with self.t.fullscreen():
            print(self.t.clear())
            if self.wm.has_wallet():
                with self.t.location(0, 7):
                    logging.error(
                        self.t.bold_reverse(
                            "Wallet already exists, cannot generate new wallet"
                        )
                    )
                press_any_key_to_return(self.t, "to the wallet menu")
                return
            passphrase = get_user_input(
                self.t,
                1,
                "Enter a passphrase for your new wallet (make it unique but memorable!). This is optional - if you do not want to set a passphrase, leave blank",
            )
            encryption_password = get_user_input(
                self.t,
                3,
                "Enter a password to encrypt your wallet file. This is optional - if you do not want to encrypt your wallet file, leave blank. Remember this password, as you will need it to access your wallet.",
            )
            with self.t.location(0, 7):
                print("Wallet passphrase: " + passphrase)
                print("Encryption password: " + encryption_password)
            yn = get_user_input(
                self.t, 10, "Are you sure you want to generate a new wallet? (y/n)"
            )
            if yn == "y":
                words, bin_seed, entropy = self.wm.generate(
                    passphrase, encryption_password
                )
                logging.info("Wallet generated")
                print(
                    """
    *******************************************************************************
    Your wallet has been generated!
    INSTRUCTIONS: WRITE DOWN THE FOLLOWING WORDS TO BACKUP YOUR WALLET AND STORE IN A SAFE AND SECURE OFFLINE LOCATION.
    THIS BACKUP SEED PHRASE WILL BE USED TO RECOVER YOUR WALLET IF YOU LOSE ACCESS TO THIS DEVICE.
    THIS BACKUP PHRASE WILL NOT BE SAVED ANYWHERE ON THIS DEVICE. FAILURE TO SECURE THIS BACKUP SEED PHRASE MAY CAUSE YOU TO LOSE YOUR BITCOIN.
    !!DO NOT FORGET THESE!!
    *******************************************************************************
    """
                )
                print("*" * 20)
                print(words)
                print("*" * 20)
                print(f"\nThe binary seed from the mnemonic is: {bin_seed.hex()}")
                print(f"Entropy = {entropy}\n")
            else:
                logging.warn("Wallet generation cancelled")
            press_any_key_to_return(self.t, UIStrings.to_menu(UIStrings.WALLET_MENU))

    def show(self):

        menu_options = [
            ("Show bitcoin address", self.show_addr),
            ("Recover bitcoin wallet", self.recover_wallet),
            ("Generate new wallet", self.generate_wallet),
            ("Back to main menu", lambda: None),
        ]
        generic_menu(menu_options, UIStrings.WALLET_MENU)
