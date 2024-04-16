# Features

## Ideas

* Lookup an address balance given a public key or xpub
* Implement a notification system for transaction confirmations
* Add support for other languages (in UI and for seed phrase generation)
* Use a different address per transaction (following BIP 32)
* Implement multi-signature wallets for added security
* Integrate with hardware wallets
* Add a feature to estimate transaction fees
* Implement a backup system for the wallet
* Add a feature to import/export private keys
* Add a feature to set custom transaction fees (make this configurable by the user)
* Implement a light/dark mode for the UI
* Add a feature to show the current cryptocurrency market rates (could use my other project)
* Implement a feature to schedule recurring transactions
* Implement a privacy mode that hides balance and transaction amounts
* Add a feature to automatically update the wallet software.

In progress:

* Make a terminal UI using blessed
* Add a feature to export transaction history to a CSV file
* Encrypt wallet seed file

GitHub Copilot: Implementing a backup system for a wallet in a cryptocurrency application involves creating a way to save and restore the private keys which control access to the cryptocurrency. Here's a general approach:

1. **Encrypt the private key(s)**: The private keys should be encrypted for security. This could be done using a password entered by the user.

2. **Export the encrypted key(s)**: The encrypted keys could be exported to a file. This file is what the user will use to restore their wallet.

3. **Import the encrypted key(s)**: Create a feature that allows the user to import their encrypted keys from a file. After entering the correct password, the keys should be decrypted and loaded into the wallet.

Here's a simple pseudocode:

```pseudocode
function backupWallet(password):
    encryptedKeys = encrypt(privateKeys, password)
    saveToFile(encryptedKeys)

function restoreWallet(file, password):
    encryptedKeys = loadFromFile(file)
    privateKeys = decrypt(encryptedKeys, password)
    loadKeysIntoWallet(privateKeys)
```

Please note that this is a simplified version of what you would need to do. Cryptography is complex and making mistakes can lead to lost or stolen cryptocurrency. It's recommended to use well-tested libraries for the encryption and decryption process, and to have your code reviewed by a security expert.

Also, this pseudocode doesn't include any error handling. In a real implementation, you would need to handle potential errors, such as the user entering an incorrect password, the file not existing, etc.

Bugs to fix:

Completed:

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

Bugs fixed:
✅ Off by one error in contact selection
