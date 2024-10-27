from sqlalchemy.sql.schema import ForeignKey
from .database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship


class DbUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    items = relationship('DbPost', back_populates='user')
    likes = relationship("DbLike", back_populates="user", cascade="all, delete-orphan")
    followers = relationship("DbSubscription", foreign_keys="[DbSubscription.followed_id]", back_populates="followed", cascade="all, delete-orphan")
    following = relationship("DbSubscription", foreign_keys="[DbSubscription.follower_id]", back_populates="follower", cascade="all, delete-orphan")

class DbPost(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    image_url_type = Column(String)
    caption = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('DbUser', back_populates='items')
    comments = relationship('DbComment', back_populates='post')
    likes = relationship("DbLike", back_populates="post", cascade="all, delete-orphan")
    @property
    def like_count(self):
        return len(self.likes)

class DbComment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    username = Column(String)
    timestamp = Column(DateTime)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship("DbPost", back_populates="comments")


class DbSubscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey('user.id'))
    followed_id = Column(Integer, ForeignKey('user.id'))

    follower = relationship("DbUser", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("DbUser", foreign_keys=[followed_id], back_populates="followers")

class DbLike(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"), nullable=False)

    user = relationship("DbUser", back_populates="likes")
    post = relationship("DbPost", back_populates="likes")