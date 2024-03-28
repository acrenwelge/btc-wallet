# btc-wallet

[![PyPI - Version](https://img.shields.io/pypi/v/btc-wallet.svg)](https://pypi.org/project/btc-wallet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/btc-wallet.svg)](https://pypi.org/project/btc-wallet)

With this proof-of-concept bitcoin wallet, you can:

* Generate a mnemonic seed phrase for a new HD wallet
* Restore an existing HD wallet from seed phrase
* Store and manage a list of contacts' bitcoin addresses
* Send bitcoin to your contacts

**THIS APPLICATION IS A PROOF OF CONCEPT - PLEASE DO NOT USE FOR MANAGING REAL BITCOIN ON MAINNET**

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install btc-wallet
```

## Run Locally

```console
cd btc-wallet
pipx install hatch
hatch run python start.py
```

## Standards Compliance

* [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
* [BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)

## Built With

* [Hatch](https://hatch.pypa.io/latest/)
* [bit](https://pypi.org/project/bit/)
* [Python-mnemonic](https://github.com/trezor/python-mnemonic)
* [qrcode](https://pypi.org/project/qrcode/)
* [Blockstream API](https://github.com/Blockstream/esplora/blob/master/API.md#transaction-format)

## License

This program is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
