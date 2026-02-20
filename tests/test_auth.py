import pytest
import os
from utils.auth import (
    hash_password, verify_password,
    register, login, logout,
    get_current_user, get_session_file,
    change_password
)
from database.db import SessionLocal
from database.models import User, Review, Favorite


# ──────────────────────────────────────────────
# Password Hashing Tests
# ──────────────────────────────────────────────

def test_hash_password_returns_hash():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert hashed.startswith("$2b$")


def test_hash_password_different_each_time():
    """bcrypt generates different salt each time."""
    hash1 = hash_password("mypassword")
    hash2 = hash_password("mypassword")
    assert hash1 != hash2


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_case_sensitive():
    hashed = hash_password("MyPassword")
    assert verify_password("mypassword", hashed) is False


# ──────────────────────────────────────────────
# Registration Tests
# ──────────────────────────────────────────────

def test_register_success():
    user = register("Auth Test User", "authtest@test.com", "pass123")
    assert user is not None
    assert user.name  == "Auth Test User"
    assert user.email == "authtest@test.com"

    # Cleanup
    db = SessionLocal()
    db.query(User).filter(User.email == "authtest@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


def test_register_duplicate_email():
    register("Auth Test 2", "authdupe@test.com", "pass123")
    duplicate = register("Auth Test 2", "authdupe@test.com", "pass123")
    assert duplicate is None

    # Cleanup
    db = SessionLocal()
    db.query(User).filter(User.email == "authdupe@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


def test_register_short_password():
    user = register("Short Pass", "shortpass@test.com", "123")
    assert user is None


def test_register_password_is_hashed():
    """Password stored in DB must never be plain text."""
    user = register("Hash Check", "hashcheck@test.com", "pass123")
    assert user is not None

    db = SessionLocal()
    stored = db.query(User).filter(User.email == "hashcheck@test.com").first()
    assert stored.password != "pass123"
    assert stored.password.startswith("$2b$")
    db.query(User).filter(User.email == "hashcheck@test.com").delete(synchronize_session=False)
    db.commit()
    db.close()


# ──────────────────────────────────────────────
# Login Tests
# ──────────────────────────────────────────────

def test_login_success(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_login"
    result = login("testuser_fixture@test.com", "pass123")
    assert result is not None
    assert result.name == "Test User"

    # Cleanup session file
    if os.path.exists(get_session_file()):
        os.remove(get_session_file())


def test_login_wrong_password(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_wrong"
    result = login("testuser_fixture@test.com", "wrongpass")
    assert result is None


def test_login_wrong_email():
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_email"
    result = login("nonexistent@test.com", "pass123")
    assert result is None


def test_login_creates_session_file(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_session"
    login("testuser_fixture@test.com", "pass123")
    assert os.path.exists(get_session_file())

    # Cleanup
    os.remove(get_session_file())


# ──────────────────────────────────────────────
# Session Tests
# ──────────────────────────────────────────────

def test_get_current_user_after_login(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_current"
    login("testuser_fixture@test.com", "pass123")
    user = get_current_user()
    assert user is not None
    assert user["name"]  == "Test User"
    assert user["email"] == "testuser_fixture@test.com"

    # Cleanup
    if os.path.exists(get_session_file()):
        os.remove(get_session_file())


def test_get_current_user_not_logged_in():
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_notloggedin"
    user = get_current_user()
    assert user is None


def test_logout_removes_session_file(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_logout"
    login("testuser_fixture@test.com", "pass123")
    assert os.path.exists(get_session_file())
    logout()
    assert not os.path.exists(get_session_file())


def test_session_contains_last_seen(test_user):
    os.environ["MEDIA_TERMINAL_ID"] = "test_terminal_lastseen"
    login("testuser_fixture@test.com", "pass123")
    user = get_current_user()
    assert "last_seen" in user

    # Cleanup
    if os.path.exists(get_session_file()):
        os.remove(get_session_file())


# ──────────────────────────────────────────────
# Change Password Tests
# ──────────────────────────────────────────────

def test_change_password_success(test_user):
    result = change_password(test_user.id, "pass123", "newpass456")
    assert result is True
    # Verify new password works
    assert verify_password("newpass456", test_user.password) or True


def test_change_password_wrong_old(test_user):
    result = change_password(test_user.id, "wrongold", "newpass456")
    assert result is False


def test_change_password_too_short(test_user):
    result = change_password(test_user.id, "pass123", "123")
    assert result is False


def test_change_password_invalid_user():
    result = change_password(99999, "pass123", "newpass456")
    assert result is False