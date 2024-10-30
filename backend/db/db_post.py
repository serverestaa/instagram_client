from fastapi import HTTPException, status

from db.db_search import index_data_to_es, create_index_action, es
from routers.schemas import PostBase
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from db.models import DbPost, DbLike, DbUser
import datetime


def create(db: Session, request: PostBase):
    new_post = DbPost(
        image_url=request.image_url,
        image_url_type=request.image_url_type,
        caption=request.caption,
        timestamp=datetime.datetime.now(),
        user_id=request.creator_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    index_data_to_es(db, new_data=create_index_action("posts", new_post.id, {
        "content": new_post.caption,
        "timestamp": new_post.timestamp.isoformat(),
        "username": new_post.user.username
    }))
    return new_post


def get_all(db: Session):
    return db.query(DbPost).all()


def delete(db: Session, id: int, user_id: int):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')
    if post.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only post creator can delete post')

    db.delete(post)
    db.commit()

    try:
        es.delete(index="posts", id=id, ignore=[404])
    except Exception as e:
        print(f"Error deleting post from Elasticsearch: {e}")
    return 'ok'


def get_posts_by_user_id(db: Session, user_id: int):
    return db.query(DbPost).filter(DbPost.user_id == user_id).all()


def get_post_by_id(db: Session, post_id: int):
    return (
        db.query(DbPost)
        .options(joinedload(DbPost.likes).joinedload(DbLike.user))
        .filter(DbPost.id == post_id)
        .first()
    )


def add_like(db: Session, user_id: int, post_id: int):
    like = DbLike(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def remove_like(db: Session, user_id: int, post_id: int):
    like = db.query(DbLike).filter(DbLike.user_id == user_id, DbLike.post_id == post_id).first()
    if like:
        db.delete(like)
        db.commit()
    return like


def get_like_count(db: Session, post_id: int):
    return db.query(DbLike).filter(DbLike.post_id == post_id).count()


def user_has_liked(db: Session, user_id: int, post_id: int):
    return db.query(DbLike).filter(DbLike.user_id == user_id, DbLike.post_id == post_id).first() is not None


def get_likes_for_post(db: Session, post_id: int):
    return (
        db.query(DbUser)
        .join(DbLike, DbLike.user_id == DbUser.id)
        .filter(DbLike.post_id == post_id)
        .all()
    )
