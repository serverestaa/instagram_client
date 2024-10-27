from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from routers.schemas import PostBase, PostDisplay, LikeListResponse
from db.database import get_db
from db import db_post
from typing import List
import random
import string
import shutil
from routers.schemas import UserAuth

router = APIRouter(
    prefix='/post',
    tags=['post']
)

image_url_types = ['absolute', 'relative']


@router.post('', response_model=PostDisplay)
def create(request: PostBase, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if not request.image_url_type in image_url_types:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Parameter image_url_type can only take values 'absolute' or 'relative'.")
    return db_post.create(db, request)


@router.get('/all', response_model=List[PostDisplay])
def posts(db: Session = Depends(get_db)):
    return db_post.get_all(db)

@router.get("/user/{user_id}", response_model=List[PostDisplay])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    posts = db_post.get_posts_by_user_id(db, user_id=user_id)
    if posts is None:
        raise HTTPException(status_code=404, detail="Posts not found")
    return posts


@router.post('/image')
def upload_image(image: UploadFile = File(...), current_user: UserAuth = Depends(get_current_user)):
    sanitized_filename = image.filename.replace(" ", "_")

    letters = string.ascii_letters
    rand_str = ''.join(random.choice(letters) for i in range(6))
    new = f'_{rand_str}.'
    filename = new.join(sanitized_filename.rsplit('.', 1))
    path = f'images/{filename}'

    with open(path, "w+b") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {'filename': path}


@router.get('/delete/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return db_post.delete(db, id, current_user.id)

@router.post("/{post_id}/like")
def like_post(post_id: int, user_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if db_post.user_has_liked(db, user_id, post_id):
        raise HTTPException(status_code=400, detail="User has already liked this post.")
    return db_post.add_like(db, user_id, post_id)

@router.delete("/{post_id}/unlike")
def unlike_post(post_id: int, user_id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if not db_post.user_has_liked(db, user_id, post_id):
        raise HTTPException(status_code=400, detail="User has not liked this post.")
    return db_post.remove_like(db, user_id, post_id)

@router.get("/{post_id}/likes/count")
def get_post_likes_count(post_id: int, db: Session = Depends(get_db)):
    return {"count": db_post.get_like_count(db, post_id)}


@router.get("/{post_id}/likes", response_model=LikeListResponse)
def get_users_liked(post_id: int, db: Session = Depends(get_db)):
    users = db_post.get_likes_for_post(db, post_id)
    return {"likes": [{"user_id": user.id, "username": user.username} for user in users]}
