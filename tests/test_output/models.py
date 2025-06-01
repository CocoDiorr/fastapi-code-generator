
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(
        Integer
        
        , primary_key=True
        , nullable=False
    )
    username = Column(
        String(50)
        
        , primary_key=False
        , nullable=False
    )
    email = Column(
        String(100)
        
        , primary_key=False
        , nullable=False
    )
    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"
    id = Column(
        Integer
        
        , primary_key=True
        , nullable=False
    )
    title = Column(
        String(200)
        
        , primary_key=False
        , nullable=False
    )
    content = Column(
        String
        
        , primary_key=False
        , nullable=False
    )
    user_id = Column(
        Integer
        , ForeignKey("users.id")
        , primary_key=False
        , nullable=False
    )
    user = relationship(
        "User",
        back_populates="posts"
    )

