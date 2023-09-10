from dataclasses import dataclass


@dataclass
class UserRep:
    id: int
    username: str
    email: str
    role: str
    permissions: list
    created_at: str
    updated_at: str
