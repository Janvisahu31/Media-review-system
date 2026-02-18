from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///media_review.db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """Dependency that provides a DB session and ensures it closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_db():
    """Create all tables if they don't exist yet."""
    from database import models  # noqa: F401 — import so Base sees the models
    Base.metadata.create_all(bind=engine)


