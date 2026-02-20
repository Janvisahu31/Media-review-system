from database.db import SessionLocal
from database.models import User
from utils.auth import hash_password


def add_user(name: str, email: str, password: str):
    """Add a new user to the database."""
    db = SessionLocal()
    try:
        # Check if email already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ User with email '{email}' already exists.")
            return None
        
        hashed = hash_password(password)
        user = User(name=name, email=email, password=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ User '{name}' added successfully with ID {user.id}")
        return user

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding user: {e}")
        return None

    finally:
        db.close()


def get_user_by_id(user_id: int):
    """Fetch a user by their ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ No user found with ID {user_id}")
            return None
        return user

    finally:
        db.close()


def get_all_users():
    """Fetch all users."""
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def get_user_by_email(email: str):
    """Fetch a user by email."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()