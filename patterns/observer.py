from database.db import SessionLocal
from database.models import Favorite, Review, Media, User
from utils.auth import update_last_seen
from datetime import datetime

class Observer:
    def notify(self, media_title: str, reviewer_name: str, rating: float, comment: str):
        raise NotImplementedError("Observer must implement notify()")


class UserObserver(Observer):
    def __init__(self, user_name: str):
        self.user_name = user_name

    def notify(self, media_title: str, reviewer_name: str, rating: float, comment: str):
        print(
            f"\n🔔 New review on '{media_title}'\n"
            f"   Reviewer : {reviewer_name}\n"
            f"   Rating   : {rating}/10\n"
            f"   Comment  : {comment}"
        )


class ReviewSubject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def notify_all(self, media_title: str, reviewer_name: str, rating: float, comment: str):
        for observer in self._observers:
            observer.notify(media_title, reviewer_name, rating, comment)


def add_favorite(user_id: int, media_id: int):
    """Add a media to user's favorites."""
    db = SessionLocal()
    try:
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.media_id == media_id
        ).first()
        if existing:
            print("❌ Already in favorites.")
            return None

        user  = db.query(User).filter(User.id == user_id).first()
        media = db.query(Media).filter(Media.id == media_id).first()

        if not user:
            print(f"❌ No user found with ID {user_id}")
            return None
        if not media:
            print(f"❌ No media found with ID {media_id}")
            return None

        favorite = Favorite(user_id=user_id, media_id=media_id)
        db.add(favorite)
        db.commit()
        print(f"✅ '{media.title}' added to {user.name}'s favorites!")
        return favorite

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        return None

    finally:
        db.close()


def get_notifications(logged_in_user_id: int, last_seen:str):
    """
    Show only NEW notifications since last_seen timestamp.
    After showing, update last_seen so they won't show again.
    """
    db = SessionLocal()
    try:
        # Get logged in user
        user = db.query(User).filter(User.id == logged_in_user_id).first()
        if not user:
            print("❌ User not found.")
            return
        
        # Parse last_seen timestamp
        last_seen_dt = datetime.fromisoformat(last_seen)

        # Find all media this user has favorited
        favorites = db.query(Favorite).filter(
            Favorite.user_id == logged_in_user_id
        ).all()

        if not favorites:
            print(f"❌ You haven't favorited any media yet.")
            print(f"   Run: python media_review.py --favorite <media_id>")
            return

        print(f"\n🔔 Notifications for {user.name}:\n")

        found_any = False

        for fav in favorites:
            media = db.query(Media).filter(Media.id == fav.media_id).first()
            if not media:
                continue

            # Get latest reviews on this media (excluding user's own reviews)
            new_reviews = (
                db.query(Review)
                .filter(
                    Review.media_id == fav.media_id,
                    Review.user_id != logged_in_user_id,
                    Review.created_at > last_seen_dt  
                    # exclude own reviews
                )
                .order_by(Review.created_at.desc())
                .limit(3)
                .all()
            )

            if not new_reviews:
                continue

            found_any = True

            # Use Observer pattern to display notifications
            subject = ReviewSubject()
            subject.attach(UserObserver(user.name))

            for review in new_reviews:
                reviewer = db.query(User).filter(User.id == review.user_id).first()
                subject.notify_all(
                    media_title=media.title,
                    reviewer_name=reviewer.name if reviewer else "Unknown",
                    rating=review.rating,
                    comment=review.comment
                )

        if not found_any:
            print(" You're all caught up! No new reviews on your favorites.")

        update_last_seen()
        print(f"\n📅 Last checked: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    finally:
        db.close()