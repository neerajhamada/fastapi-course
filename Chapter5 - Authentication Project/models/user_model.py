from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique = True)
    college: str

    # One user can have many books
    books: list["Book"] = Relationship(back_populates="owner")

# Request body for creating a User
class UserCreate(SQLModel):
    name: str
    email: str
    college: str

# Response for getting a User
class UserRead(SQLModel):
    id: int
    name: str
    email: str
    college: str

    
# Avoid Circular Import
from models.book_model import Book
User.model_rebuild()