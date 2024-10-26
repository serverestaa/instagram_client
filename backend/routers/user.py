from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import db_user
from db.database import get_db
from db.db_user import follow_user, unfollow_user, get_user_profile
from routers.schemas import UserDisplay, UserBase, UserAuth

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.post('', response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)


@router.post("/follow/{user_id}")
def follow(user_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return follow_user(db, follower_id=current_user.id, followed_id=user_id)


@router.delete("/unfollow/{user_id}")
def unfollow(user_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return unfollow_user(db, follower_id=current_user.id, followed_id=user_id)


@router.get("/profile/{user_id}")
def profile(user_id: int, db: Session = Depends(get_db)):
    return get_user_profile(db, user_id)
