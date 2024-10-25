import datetime

from sqlalchemy.orm import Session
from db.models import DbPost
from routers.schemas import PostBase


def create(db: Session, request: PostBase):
    new_post = DbPost(
        image_url=request.image_url,
        image_url_type=request.img_url_type,
        caption=request.caption,
        timestamp=datetime.datetime.now(),
        user_id=request.creator_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)


def get_all(db: Session):
    return db.query(DbPost).all()
