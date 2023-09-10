from dataclasses import dataclass


def user_rep_factory(data, cls):
    """Set the user's data from a dictionary"""

    user = cls(data)

    return user


@dataclass
class UserRep:
    id: int
    username: str
    email: str
    role: str
    permissions: list
    created_at: str
    updated_at: str
