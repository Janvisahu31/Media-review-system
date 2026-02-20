import pytest
from services.user_service import add_user, get_user_by_id, get_user_by_email, get_all_users
from database.db import SessionLocal
from database.models import User, Review, Favorite


def test_add_user_success():
    user = add_user("Test Add", "testadd@test.com", "pass123")
    assert user is not None
    assert user.name  == "Test Add"
    assert user.email == "testadd@test.com"

    db = SessionLocal()
    db.query(User).filter(User.email == "testadd@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


def test_add_user_duplicate_email():
    add_user("Test Dupe", "testdupe_user@test.com", "pass123")
    duplicate = add_user("Test Dupe 2", "testdupe_user@test.com", "pass456")
    assert duplicate is None

    db = SessionLocal()
    db.query(User).filter(User.email == "testdupe_user@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


def test_add_user_password_is_hashed():
    user = add_user("Hash User", "hashuser@test.com", "pass123")
    assert user is not None

    db = SessionLocal()
    stored = db.query(User).filter(User.email == "hashuser@test.com").first()
    assert stored.password != "pass123"
    assert stored.password.startswith("$2b$")
    db.query(User).filter(User.email == "hashuser@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


def test_get_user_by_id_success(test_user):
    fetched = get_user_by_id(test_user.id)
    assert fetched is not None
    assert fetched.id == test_user.id


def test_get_user_by_id_not_found():
    user = get_user_by_id(99999)
    assert user is None


def test_get_user_by_email_success(test_user):
    user = get_user_by_email("testuser_fixture@test.com")
    assert user is not None
    assert user.email == "testuser_fixture@test.com"


def test_get_user_by_email_not_found():
    user = get_user_by_email("nobody@nowhere.com")
    assert user is None


def test_get_all_users_returns_list():
    users = get_all_users()
    assert isinstance(users, list)
    assert len(users) > 0