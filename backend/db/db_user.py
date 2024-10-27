from db.models import DbUser, DbSubscription
from routers.schemas import UserBase
from sqlalchemy.orm.session import Session
from db.hashing import Hash
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload


def create_user(db: Session, request: UserBase):
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with username {username} not found')
    return user


def follow_user(db: Session, follower_id: int, followed_id: int):
    if follower_id == followed_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    subscription = DbSubscription(follower_id=follower_id, followed_id=followed_id)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def unfollow_user(db: Session, follower_id: int, followed_id: int):
    if follower_id == followed_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot unfollow yourself")

    # Далее поиск и удаление подписки
    subscription = db.query(DbSubscription).filter(
        DbSubscription.follower_id == follower_id,
        DbSubscription.followed_id == followed_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    db.delete(subscription)
    db.commit()
    return {"detail": "Unfollowed successfully"}


def get_user_profile(db: Session, user_id: int):
    user = db.query(DbUser).options(joinedload(DbUser.items)).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    followers_count = db.query(DbSubscription).filter(DbSubscription.followed_id == user_id).count()
    following_count = db.query(DbSubscription).filter(DbSubscription.follower_id == user_id).count()
    posts_count = len(user.items)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "followers_count": followers_count,
        "following_count": following_count,
        "posts_count": posts_count,
        "posts": [{"id": post.id, "caption": post.caption, "timestamp": post.timestamp} for post in user.items]
    }


def get_following(db: Session, user_id: int):
    return (
        db.query(DbUser)
        .join(DbSubscription, DbSubscription.followed_id == DbUser.id)
        .filter(DbSubscription.follower_id == user_id)
        .all()
    )


def get_followers(db: Session, user_id: int):
    return (
        db.query(DbUser)
        .join(DbSubscription, DbSubscription.follower_id == DbUser.id)
        .filter(DbSubscription.followed_id == user_id)
        .all()
    )