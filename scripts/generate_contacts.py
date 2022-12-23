from bit import Key, PrivateKeyTestnet
from os.path import expanduser
import csv

# generate fake contact/address data for testing purposes
# create random public btc addresses for each name and write to .csv file
friends = ['alice','john','mark','robert','nicole']

with open(expanduser("~/.wallet/contacts.csv"),'w+') as file:
  writer = csv.writer(file)
  for friend in friends:
    k = Key()
    writer.writerow([friend, k.address])