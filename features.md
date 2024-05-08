# Features

## Ideas

* Search for transactions by date, amount, or address
* Implement a notification system for transaction confirmations
* Generate new keys until a desired address is found (for vanity addresses)
* Use a different address per transaction (following BIP 32)
* Implement multi-signature wallets for added security
* Integrate with hardware wallets
* Add lightning network support
* Autocomplete for seed phrase recovery
* Add a feature to estimate transaction fees
* Add a feature to import/export private keys
* Add a feature to set custom transaction fees (make this configurable by the user)
* Add a feature to show the current cryptocurrency market rates (could use my other project)
* Implement a feature to schedule recurring transactions
* Implement a privacy mode that hides balance and transaction amounts
* Add a feature to automatically update the wallet software
* Add support for other languages (in UI and for seed phrase generation)

## In progress

* Make user settings configurable and save them to a file

## Completed Features

* Login
* Recover from seed phrase backup
* Generate new wallet
* Contact list
  * Maintain list of contacts with addresses
  * View contacts + addresses
  * Add new contacts
* View QR code for btc addresses
* TEST vs PROD modes for testnet vs mainnet
* View transaction history
* See BTC balance
* Send BTC
* Read user password from environment
* Change app password
* Update contacts
* Delete contacts
* BTC address verification (any time a btc address is input)
* Timeout - logout user after a certain amount of time of inactivity
* Make a terminal UI using blessed
* Add a feature to export transaction history to a CSV file
* Encrypt wallet seed file
* Cache the balance of an address to avoid querying the blockchain every time, and set a TTL for the cache
* Lookup an address balance given a public key or xpub
* Light / dark mode (user theme setting)

## Defects

### Known Bugs

### Bugs Fixed

✅ Off by one error in contact selection
✅ View txs should be blank when no wallet exists
✅ Seed should be encrypted when recovering from seed phrase
