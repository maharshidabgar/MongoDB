from sqlmodel import Session, select
from models import Room, Booking, User
from datetime import date

def get_room_by_number(session: Session, number: str):
    return session.exec(select(Room).where(Room.number == number)).first()

def list_rooms(session: Session, offset: int = 0, limit: int = 20):
    return session.exec(select(Room).offset(offset).limit(limit)).all()

def is_room_available(session: Session, room_id: int, check_in: date, check_out: date):
    overlapping = session.exec(
        select(Booking).where(
            Booking.room_id == room_id,
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    ).all()
    return len(overlapping) == 0

def create_booking(session: Session, user: User, room: Room, check_in: date, check_out: date):
    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValueError("Invalid date range")
    if not is_room_available(session, room.id, check_in, check_out):
        raise ValueError("Room not available in that range")
    total = nights * room.price_per_night
    booking = Booking(
        user_id=user.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        total_price=total,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking
