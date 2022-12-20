import requests
import json
import os

# read endpoint either from env variable or from local file
url = None
try:
  url = os.environ["QUICKNODE_API"]
except KeyError:
  with open('testnet-endpoint.txt') as f:
    url = f.read()

class NodeAPI:
  payload = json.dumps({
    "method": "getblockcount"
  })
  headers = {
    'Content-Type': 'application/json'
  }

  def _send_http_req(self):
    response = requests.request("POST", url, headers=self.headers, data=self.payload)
    print(response.text)
