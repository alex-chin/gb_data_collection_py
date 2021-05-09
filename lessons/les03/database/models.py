from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Table

Base = declarative_base()


class IdMixin:
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", BigInteger, ForeignKey("post.id")),
    Column("tag_id", BigInteger, ForeignKey("tag.id"))
)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class Post(Base, IdMixin, UrlMixin):
    __tablename__ = "post"
    title = Column(String(256), nullable=False, unique=False)
    author_id = Column(BigInteger, ForeignKey("author.id"))
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)


class Author(Base, IdMixin, UrlMixin):
    __tablename__ = "author"
    name = Column(String(150), nullable=False)


class Tag(Base, UrlMixin, IdMixin):
    __tablename__ = "tag"
    name = Column(String(150), nullable=False)
    posts = relationship(Post, secondary=tag_post)
