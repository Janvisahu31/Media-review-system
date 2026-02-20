import pytest
import os
from database.db import initialize_db, SessionLocal
from database.models import User, Media, Review, Favorite


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialize DB once for entire test session."""
    initialize_db()
    yield


@pytest.fixture
def db():
    """Provide a DB session and rollback after each test."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_user(db):
    """Create a test user and clean up after test."""
    from utils.auth import hash_password
    user = User(
        name="Test User",
        email="testuser_fixture@test.com",
        password=hash_password("pass123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(Review).filter(Review.user_id == user.id).delete(synchronize_session=False)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()


@pytest.fixture
def test_user_2(db):
    """Create a second test user."""
    from utils.auth import hash_password
    user = User(
        name="Test User 2",
        email="testuser2_fixture@test.com",
        password=hash_password("pass456")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(Review).filter(Review.user_id == user.id).delete(synchronize_session=False)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()


@pytest.fixture
def test_media(db):
    """Create a test media item and clean up after test."""
    from database.models import MediaType
    media = Media(
        title="Test Media Fixture",
        media_type=MediaType.MOVIE,
        genre="Action",
        release_year=2022,
        creator="Test Director"
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    yield media
    db.query(Review).filter(Review.media_id == media.id).delete(synchronize_session=False)
    db.query(Favorite).filter(Favorite.media_id == media.id).delete(synchronize_session=False)
    db.delete(media)
    db.commit()


@pytest.fixture
def test_media_2(db):
    """Create a second test media item."""
    from database.models import MediaType
    media = Media(
        title="Test Media Fixture 2",
        media_type=MediaType.SONG,
        genre="Action",
        release_year=2021,
        creator="Test Artist"
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    yield media
    db.query(Review).filter(Review.media_id == media.id).delete(synchronize_session=False)
    db.query(Favorite).filter(Favorite.media_id == media.id).delete(synchronize_session=False)
    db.delete(media)
    db.commit()


@pytest.fixture
def test_review(db, test_user, test_media):
    """Create a test review."""
    review = Review(
        user_id=test_user.id,
        media_id=test_media.id,
        rating=8.5,
        comment="Test comment"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    yield review
    db.delete(review)
    db.commit()