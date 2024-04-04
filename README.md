# btc-wallet

[![PyPI - Version](https://img.shields.io/pypi/v/btc-wallet.svg)](https://pypi.org/project/btc-wallet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/btc-wallet.svg)](https://pypi.org/project/btc-wallet)

With this proof-of-concept bitcoin wallet, you can:

* Generate a mnemonic seed phrase for a new HD wallet
* Restore an existing HD wallet from seed phrase
* Store and manage a list of contacts' bitcoin addresses
* Send bitcoin to your contacts

> **THIS APPLICATION IS A PROOF OF CONCEPT - PLEASE DO NOT USE FOR MANAGING REAL BITCOIN ON MAINNET**

-----

## Table of Contents

* [Installation](#installation)
* [License](#license)

## Installation

```bash
pip install btc-wallet
```

## Run Locally

```bash
cd btc-wallet
pipx install hatch
hatch run python start.py
```

### Test vs Prod Modes

By default, the application runs in test mode, which uses testnet. To run in prod mode and use mainnet, set the mode flag to `prod`:

```bash
hatch shell
python start.py --mode prod
```

### Get Testnet Bitcoin

This may or may not work, in my experience...

* [Testnet Faucet](https://bitcoinfaucet.uo1.net/send.php)

Alternatively, I've [found a project](https://github.com/freewil/bitcoin-testnet-box/tree/master) that lets you mock a testnet locally.

## Standards Compliance

* [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
* [BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)

## Built With

* [Hatch](https://hatch.pypa.io/latest/)
* [bit](https://pypi.org/project/bit/)
* [bip32](https://pypi.org/project/bip32/)
* [Python-mnemonic](https://github.com/trezor/python-mnemonic)
* [qrcode](https://pypi.org/project/qrcode/)
* [Blockstream API](https://github.com/Blockstream/esplora/blob/master/API.md#transaction-format)

## License

This program is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
