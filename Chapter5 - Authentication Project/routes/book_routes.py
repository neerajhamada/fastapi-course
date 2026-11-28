from fastapi import Depends, HTTPException, APIRouter, Query
from database import get_session
from sqlmodel import Session, select
from typing import Optional
from models.book_model import Book, BookCreate, BookRead, BookUpdate
from models.user_model import User
from auth import verify_api_key

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/",response_model=list[BookRead])
def list_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(Book).where(Book.is_sold == False)

    if title:
        query = query.where(Book.title.contains(title))
    if author:
        query = query.where(Book.author.contains(author))

    books = session.exec(query).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books available")
    return books


@router.post("/", response_model=BookRead)
def create_book(
    book_data: BookCreate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    # Verify owner exists
    owner = session.get(User, book_data.user_id)
    if not owner:
        raise HTTPException(status_code=404, detail=
        f"Cannot create book: User with ID {book_data.user_id} does not exist"
        )

    # Prevent duplicate titles
    existing_book = session.exec(
        select(Book).where(
            Book.title == book_data.title,
            Book.author == book_data.author
            )).first()
    if existing_book:
        raise HTTPException(status_code=409,detail=f"Book with title '{book_data.title}' of author {book_data.author} already exists")

    new_book = Book.model_validate(book_data)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    updates: BookUpdate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404,detail=f"Book with ID {book_id} not found")

    book_data = updates.model_dump(exclude_unset=True)
    if not book_data:
        raise HTTPException(status_code=400,detail="At least one book field must be provided")

    for key, value in book_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@router.patch("/{book_id}/sold", response_model=BookRead)
def mark_book_sold(
    book_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404,detail=f"Book with ID {book_id} not found")

    db_book.is_sold = True
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404,detail=f"Book with ID {book_id} not found")
    return book