import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database.db import Base


class MediaType(enum.Enum):
    MOVIE    = "movie"
    WEB_SHOW = "web_show"
    SONG     = "song"


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reviews    = relationship("Review",   back_populates="user")
    favorites  = relationship("Favorite", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} name={self.name}>"


class Media(Base):
    __tablename__ = "media"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)
    media_type   = Column(Enum(MediaType), nullable=False)
    genre        = Column(String(100))
    release_year = Column(Integer)
    creator      = Column(String(150))   # director for movies/shows, artist for songs
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reviews      = relationship("Review",   back_populates="media")
    favorites    = relationship("Favorite", back_populates="media")

    def __repr__(self):
        return f"<Media id={self.id} title={self.title} type={self.media_type.value}>"


class Review(Base):
    __tablename__ = "reviews"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"),  nullable=False)
    media_id   = Column(Integer, ForeignKey("media.id"),  nullable=False)
    rating     = Column(Float,   nullable=False)           # 1.0 – 10.0
    comment    = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user       = relationship("User",  back_populates="reviews")
    media      = relationship("Media", back_populates="reviews")

    def __repr__(self):
        return f"<Review user={self.user_id} media={self.media_id} rating={self.rating}>"


class Favorite(Base):
    __tablename__ = "favorites"

    id       = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey("users.id"),  nullable=False)
    media_id = Column(Integer, ForeignKey("media.id"),  nullable=False)

    user     = relationship("User",  back_populates="favorites")
    media    = relationship("Media", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite user={self.user_id} media={self.media_id}>"