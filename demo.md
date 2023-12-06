Total time: 20 min

## Intro ~ 2 min

1. Introduce myself (note: emphasize this is just a personal project)
2. Explain why I started this project
  - Learn Python, apply learnings from bitcoin book
  - This is a proof-of-concept bitcoin wallet
3. What is Bitcoin?
  - What is a software wallet?

## Demo ~ 15 min 

1. Run in test mode - explain testnet vs mainnet
2. Generate new wallet
3. Record recovery phrase - explain how this is used to generate a binary seed, portability via BIP39
4. View wallet info + balance
5. Get testnet bitcoin from faucet
6. View updated balance + transactions
7. View contacts (explain public key vs private key), add testnet faucet as a contact
8. Send bitcoin back to faucet
9. View updated wallet info + balance
10. Delete `~/.wallet/testseed.txt` and copy recovery phrase from step 3
11. Restart the program and show that the wallet is empty
12. Restore wallet from old seed phrase and show balance is restored

## Questions ~ 3 min
1. Explain - using file persistance for storing wallet/contact data