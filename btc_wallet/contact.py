from dataclasses import dataclass, field

@dataclass
class Contact:
  id: int
  name: str
  addr: str