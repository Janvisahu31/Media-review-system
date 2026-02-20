import pytest
from patterns.observer import add_favorite, get_notifications, ReviewSubject, UserObserver
from database.db import SessionLocal
from database.models import Favorite, Review
import os


def test_add_favorite_success(test_user, test_media):
    result = add_favorite(test_user.id, test_media.id)
    assert result is not None

    db = SessionLocal()
    fav = db.query(Favorite).filter(
        Favorite.user_id  == test_user.id,
        Favorite.media_id == test_media.id
    ).first()
    assert fav is not None
    db.close()


def test_add_favorite_duplicate(test_user, test_media):
    add_favorite(test_user.id, test_media.id)
    duplicate = add_favorite(test_user.id, test_media.id)
    assert duplicate is None


def test_add_favorite_invalid_user(test_media):
    result = add_favorite(99999, test_media.id)
    assert result is None


def test_add_favorite_invalid_media(test_user):
    result = add_favorite(test_user.id, 99999)
    assert result is None


def test_observer_notify(capsys):
    """Test that UserObserver prints notification correctly."""
    observer = UserObserver("Alice")
    observer.notify("Inception", "Bob", 9.0, "Amazing!")
    captured = capsys.readouterr()
    assert "Inception" in captured.out
    assert "Bob"       in captured.out
    assert "9.0"       in captured.out
    assert "Amazing!"  in captured.out


def test_review_subject_notify_all(capsys):
    """Test that ReviewSubject notifies all attached observers."""
    subject = ReviewSubject()
    subject.attach(UserObserver("Alice"))
    subject.attach(UserObserver("Bob"))
    subject.notify_all("Dark", "Charlie", 8.5, "Mind blowing!")
    captured = capsys.readouterr()
    assert "Dark"         in captured.out   
    assert "Charlie"      in captured.out  
    assert "8.5"          in captured.out   
    assert "Mind blowing" in captured.out   
    assert captured.out.count("Dark") == 2


def test_review_subject_no_observers(capsys):
    """Test that empty subject doesn't crash."""
    subject = ReviewSubject()
    subject.notify_all("Test", "User", 7.0, "Ok")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_get_notifications_no_favorites(test_user):
    """User with no favorites gets appropriate message."""
    os.environ["MEDIA_TERMINAL_ID"] = "test_notif_terminal"
    from utils.auth import login
    login("testuser_fixture@test.com", "pass123")
    user = {"user_id": test_user.id, "last_seen": "2000-01-01T00:00:00"}
    get_notifications(user["user_id"], user["last_seen"])


def test_get_notifications_with_favorites(test_user, test_user_2, test_media, test_review):
    """User with favorites gets notifications for new reviews."""
    add_favorite(test_user.id, test_media.id)
    last_seen = "2000-01-01T00:00:00"
    get_notifications(test_user.id, last_seen)