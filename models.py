from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = False
    bookings: list["Booking"] = Relationship(back_populates="user")

class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True, unique=True)
    type: str  # e.g., single, double, suite
    price_per_night: float
    description: Optional[str] = None
    bookings: list["Booking"] = Relationship(back_populates="room")

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="room.id")
    check_in: date
    check_out: date
    total_price: float

    user: Optional[User] = Relationship(back_populates="bookings")
    room: Optional[Room] = Relationship(back_populates="bookings")
