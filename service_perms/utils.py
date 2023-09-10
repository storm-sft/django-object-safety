from dataclasses import dataclass


@dataclass
class UserRep:
    id: int
    username: str
    email: str
