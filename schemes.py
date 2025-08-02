from datetime import date
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class RoomCreate(BaseModel):
    number: str
    type: str
    price_per_night: float
    description: Optional[str] = None

class RoomRead(RoomCreate):
    id: int

    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    room_id: int
    check_in: date
    check_out: date

class BookingRead(BaseModel):
    id: int
    room_id: int
    user_id: int
    check_in: date
    check_out: date
    total_price: float

    class Config:
        orm_mode = True
