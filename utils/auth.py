import json
import os
from database.db import SessionLocal
from database.models import User

SESSION_FILE = "session.json"


def login(email: str, password: str):
    """Log in a user and save session."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.email == email,
            User.password == password        # plain text for now, hashed in Phase 9
        ).first()

        if not user:
            print("❌ Invalid email or password.")
            return None

        # Save session
        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user.id, "name": user.name}, f)

        print(f"✅ Welcome back, {user.name}! You are now logged in.")
        return user

    finally:
        db.close()


def logout():
    """Clear the session."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("✅ Logged out successfully.")
    else:
        print("❌ No active session found.")


def get_current_user():
    """Get the currently logged in user from session."""
    if not os.path.exists(SESSION_FILE):
        return None

    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
        return data  # returns {"user_id": ..., "name": ...}


def login_required(func):
    """
    Decorator — wraps a handler function and checks 
    if user is logged in before executing it.
    """
    def wrapper(args):
        user = get_current_user()
        if not user:
            print("❌ You must be logged in to do this.")
            print("   Run: python media_review.py --login <email> <password>")
            return
        return func(args, user)
    return wrapper