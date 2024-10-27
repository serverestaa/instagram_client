from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.oauth2 import get_current_user
from db import db_post
from db.database import get_db
from routers.schemas import LikeListResponse, UserAuth

router = APIRouter(
    prefix='/post',
    tags=['like']
)


@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if db_post.user_has_liked(db, current_user.id, post_id):
        raise HTTPException(status_code=400, detail="User has already liked this post.")
    return db_post.add_like(db, current_user.id, post_id)


@router.delete("/{post_id}/unlike")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if not db_post.user_has_liked(db, current_user.id, post_id):
        raise HTTPException(status_code=400, detail="User has not liked this post.")
    return db_post.remove_like(db, current_user.id, post_id)


@router.get("/{post_id}/likes/count")
def get_post_likes_count(post_id: int, db: Session = Depends(get_db)):
    return {"count": db_post.get_like_count(db, post_id)}


@router.get("/{post_id}/likes", response_model=LikeListResponse)
def get_users_liked(post_id: int, db: Session = Depends(get_db)):
    users = db_post.get_likes_for_post(db, post_id)
    return {"likes": [{"user_id": user.id, "username": user.username} for user in users]}
