from typing import TypedDict


class ErroPadrao(TypedDict):
    status_code: int
    description: str