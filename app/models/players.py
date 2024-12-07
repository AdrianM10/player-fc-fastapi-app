from pydantic import BaseModel
from datetime import date
from typing import Optional


class Player(BaseModel):
    name: str
    country: str
    date_of_birth: date
    team: str
    position: str
    club_number: int
    national_team_number: int


class UpdatePlayer(BaseModel):
    team: Optional[str] = None
    position: Optional[str] = None
    club_number: Optional[int] = None
    national_team_number: Optional[int] = None
