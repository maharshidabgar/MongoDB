from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import select
from datetime import timedelta
from typing import List

from database import init_db, get_session
from models import User, Room, Booking
from schemas import (
    UserCreate, UserRead, Token,
    RoomCreate, RoomRead,
    BookingCreate, BookingRead
)
from auth import (
    get_password_hash, verify_password,
    create_access_token, get_current_user, require_admin, oauth2_scheme
)
from sqlmodel import Session

app = FastAPI(title="Hotel Management API")

@app.on_event("startup")
def on_startup():
    init_db()

# Auth endpoints
@app.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_admin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/token", response_model=Token)
def login(form_data: dict = Depends()):
    # Use OAuth2PasswordRequestForm in real usage; simplified here
    from fastapi.security import OAuth2PasswordRequestForm
    form = OAuth2PasswordRequestForm(**form_data) if isinstance(form_data, dict) else form_data
    with next(get_session()) as session:
        user = session.exec(select(User).where(User.username == form.username)).first()
        if not user or not verify_password(form.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(
            {"sub": user.username},
            expires_delta=timedelta(minutes=60)
        )
        return {"access_token": access_token, "token_type": "bearer"}

# Room management
@app.post("/rooms", response_model=RoomRead)
def create_room(room_in: RoomCreate, admin=Depends(require_admin), session: Session = Depends(get_session)):
    existing = session.exec(select(Room).where(Room.number == room_in.number)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")
    room = Room.from_orm(room_in)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

@app.get("/rooms", response_model=List[RoomRead])
def get_rooms(skip: int = 0, limit: int = 20, session: Session = Depends(get_session)):
    return session.exec(select(Room).offset(skip).limit(limit)).all()

# Booking
@app.post("/bookings", response_model=BookingRead)
def book_room(booking_in: BookingCreate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    room = session.get(Room, booking_in.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    from crud import create_booking
    try:
        booking = create_booking(
            session, user, room, booking_in.check_in, booking_in.check_out
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return booking

@app.get("/my-bookings", response_model=List[BookingRead])
def my_bookings(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Booking).where(Booking.user_id == user.id)).all()
