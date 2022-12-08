from typing import List, Union

class Contact:
  def __init__(self, name: str, addr: List[str]):
    self.name = name
    self.addr = addr

  def add_btc_addr(self, addr: str):
    self.addr.append(addr)