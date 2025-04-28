import locale

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# DB settings
DATABASE_URL = "postgresql://postgres:LaneyB!74@172.29.176.78:5432/wpbd"
# DATABASE_URL = "postgresql://user:password@localhost:5432/wpbd"


# Creating an engine and session
engine = create_engine(DATABASE_URL, connect_args={"client_encoding": "UTF8"})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Defining DB model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)

    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User")
    post = relationship("Post", back_populates="comments")

Base.metadata.create_all(engine)
