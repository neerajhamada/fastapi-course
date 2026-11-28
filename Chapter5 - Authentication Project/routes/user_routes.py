from fastapi import Depends, HTTPException, APIRouter
from database import get_session
from sqlmodel import Session, select
from models.user_model import User, UserCreate, UserRead
from auth import verify_api_key

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key)
):
    existing = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"User already registered with the email {user_data.email}")

    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/users", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session) 
):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No Users found in db")
    return users

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404,detail=f"User with ID {user_id} not found")
    return user