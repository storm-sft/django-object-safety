from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserRep:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool
    date_joined: datetime
