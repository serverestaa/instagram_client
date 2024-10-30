from datetime import datetime
from sqlalchemy.orm import Session
from db.db_search import index_data_to_es, create_index_action
from db.models import DbComment
from routers.schemas import CommentBase


def create(db: Session, request: CommentBase):
    new_comment = DbComment(
        text=request.text,
        username=request.username,
        post_id=request.post_id,
        timestamp=datetime.now()
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    index_data_to_es(db, new_data=create_index_action("comments", new_comment.id, {
        "content": new_comment.text,
        "timestamp": new_comment.timestamp.isoformat()
    }))
    return new_comment


def get_all(db: Session, post_id: int):
    return db.query(DbComment).filter(DbComment.post_id == post_id).all()
