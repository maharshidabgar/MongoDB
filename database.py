from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./hotel.db"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def init_db():
    from models import User, Room, Booking
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
