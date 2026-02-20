import json
import os
import bcrypt
from database.db import SessionLocal
from database.models import User
from datetime import datetime
import glob
import platform

SESSION_FILE = "session.json"

def get_session_file():
    """
    Each terminal gets its own session file based on
    parent process ID — just like how Ubuntu handles
    multiple terminal tabs independently.
    """
    terminal_id = os.environ.get("MEDIA_TERMINAL_ID", "default")
    return f".session_{terminal_id}.json"


def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt."""
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )



def register(name: str, email: str, password: str):
    """Register a new user with a hashed password."""
    db = SessionLocal()
    try:
        # Check if email already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ Email '{email}' is already registered.")
            return None

        # Validate password strength
        if len(password) < 6:
            print("❌ Password must be at least 6 characters.")
            return None

        hashed = hash_password(password)
        user   = User(name=name, email=email, password=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Account created successfully! Welcome, {name}.")
        print(f"   You can now login with: --login {email} <password>")
        return user

    except Exception as e:
        db.rollback()
        print(f"❌ Error registering user: {e}")
        return None

    finally:
        db.close()


def login(email: str, password: str):
    """Authenticate user and create session."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print("❌ No account found with that email.")
            return None

        if not verify_password(password, user.password):
            print("❌ Incorrect password.")
            return None

        # Save session
        session_data = {
            "user_id": user.id,
            "name":    user.name,
            "email":   user.email,
            "last_seen":datetime.utcnow().isoformat(),
            "pid":os.getppid()
        }
        with open(get_session_file(), "w") as f:
            json.dump(session_data, f)

        print(f"✅ Welcome back, {user.name}! You are now logged in.")
        return user

    finally:
        db.close()


def logout():
    """Clear the current session."""
    session_file = get_session_file()
    if os.path.exists(session_file):
        os.remove(session_file)
        print("✅ Logged out successfully.")
    else:
        print("❌ No active session found in this terminal.")

def get_current_user():
    """Get logged in user for THIS terminal only."""
    session_file = get_session_file()
    if not os.path.exists(session_file):
        return None
    try:
        with open(session_file, "r") as f:
            return json.load(f)
    except Exception:
        return None

def update_last_seen():
    """Update last_seen timestamp after notifications are viewed."""
    user = get_current_user()
    if not user:
        return
    user["last_seen"] = datetime.utcnow().isoformat()
    with open(get_session_file(), "w") as f:
        json.dump(user, f)



def login_required(func):
    """
    Decorator — blocks execution if user is not logged in.
    Passes logged in user data to the handler function.
    """
    def wrapper(args):
        user = get_current_user()
        if not user:
            print("❌ You must be logged in to do this.")
            print("   Register : python media_review.py --register <name> <email> <password>")
            print("   Login    : python media_review.py --login <email> <password>")
            return
        return func(args, user)
    return wrapper


def change_password(user_id: int, old_password: str, new_password: str):
    """Change password for logged in user."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print("❌ User not found.")
            return False

        if not verify_password(old_password, user.password):
            print("❌ Old password is incorrect.")
            return False

        if len(new_password) < 6:
            print("❌ New password must be at least 6 characters.")
            return False

        user.password = hash_password(new_password)
        db.commit()
        print("✅ Password changed successfully.")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error changing password: {e}")
        return False

    finally:
        db.close()


def cleanup_sessions():
    """
    Remove session files for terminals that no longer exist.
    Call this on app startup to keep things clean.
    """
    
    if platform.system() == "Windows":
            return

    for session_file in glob.glob(".session_*.json"):
        try:
            pid = int(session_file.split("_")[1].split(".")[0])
            os.kill(pid, 0)
        except (OSError, ProcessLookupError, ValueError):
            os.remove(session_file)