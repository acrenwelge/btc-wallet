from pycoin.symbols.btc import network
from os.path import expanduser
import csv

# generate fake contact/address data for testing purposes
# deterministically create public btc addresses from the list of names and write to .csv file
friends = ['alice','john','mark','robert','nicole']

with open(expanduser("~/.wallet/contacts.csv"),'w+') as file:
  writer = csv.writer(file)
  for friend in friends:
    addr = network.keys.bip32_seed(friend.encode()).address()
    writer.writerow([friend, addr])