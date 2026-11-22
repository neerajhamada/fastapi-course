from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///theatre.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_tables():
    """Create all tables defined by SQLModel Class"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """This is the dependency that provides a database session per request"""
    with Session(engine) as session:
        yield session