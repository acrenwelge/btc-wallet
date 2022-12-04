from mnemonic import Mnemonic

words = input(f"Enter the space-separated list of words to recover your HD wallet:\n")
pw = input(f"Enter the passphrase (if there is none, leave blank):\n")
print("Recovering...")
mnemo = Mnemonic("english")
seed = mnemo.to_seed(words,passphrase=pw)
print(f"recovered seed: {seed.hex()}")
