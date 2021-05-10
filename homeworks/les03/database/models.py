import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    BigInteger,
    Text,
    Table,
    DateTime,
)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


Base = declarative_base()

# таблица связей post >>-<< tag
tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base, UrlMixin):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=True)
    # Author упоминается как строка тк объявлен ниже
    author = relationship("Author", backref="posts")
    # связь 1:n для навигации post --> tag через таблицу tag_post
    # связь post<<->>tag m:n
    tags = relationship("Tag", secondary=tag_post)


class Tag(Base, UrlMixin):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    # связь 1:n для навигации tag --> post через таблицу tag_post
    # связь post<<->>tag m:n
    posts = relationship(Post, secondary=tag_post)


class Author(Base, UrlMixin):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author", backref="comments")
    time_now = Column(DateTime)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship(Post, backref="comments")

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.created_at = dt.datetime.fromisoformat(kwargs["created_at"])
        self.hidden = kwargs["hidden"]
        self.deep = kwargs["deep"]
        self.time_now = dt.datetime.fromisoformat(kwargs["time_now"])
        self.author = kwargs["author"]