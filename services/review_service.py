from database.db import SessionLocal
from database.models import Review, Media, User
from sqlalchemy import func


def submit_review(user_id: int, media_id: int, rating: float, comment: str):
    """Submit a single review."""
    db = SessionLocal()
    try:
        # Validate rating range
        if not (1.0 <= rating <= 10.0):
            print("❌ Rating must be between 1.0 and 10.0")
            return None

        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ No user found with ID {user_id}")
            return None

        # Check media exists
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            print(f"❌ No media found with ID {media_id}")
            return None

        # Check if user already reviewed this media
        existing = db.query(Review).filter(
            Review.user_id == user_id,
            Review.media_id == media_id
        ).first()
        if existing:
            print(f"❌ User {user_id} has already reviewed '{media.title}'")
            return None

        review = Review(
            user_id=user_id,
            media_id=media_id,
            rating=rating,
            comment=comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        print(f"Review submitted for '{media.title}' by {user.name} | Rating: {rating}/10")

        notify_on_new_review(media_id, user_id, rating, comment)
        
        return review

    except Exception as e:
        db.rollback()
        print(f"❌ Error submitting review: {e}")
        return None

    finally:
        db.close()


def get_top_rated(limit: int = 5):
    """Get top rated media based on average review ratings."""
    db = SessionLocal()
    try:
        results = (
            db.query(
                Media.id,
                Media.title,
                Media.media_type,
                Media.genre,
                Media.creator,
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("review_count")
            )
            .join(Review, Media.id == Review.media_id)
            .group_by(Media.id)
            .order_by(func.avg(Review.rating).desc())
            .limit(limit)
            .all()
        )

        if not results:
            print("❌ No reviews found yet.")
            return []

        print(f"\n⭐ Top {limit} Rated Media:\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Avg Rating':<12} {'Reviews'}")
        print("-" * 65)
        for r in results:
            print(f"{r.id:<5} {r.title:<30} {r.media_type.value:<10} "
                  f"{round(r.avg_rating, 2):<12} {r.review_count}")
        return results

    finally:
        db.close()


def get_recommendations(user_id: int):
    """
    Recommend media the user hasn't reviewed yet,
    based on genres they have rated 7.0 or above.
    """
    db = SessionLocal()
    try:
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ No user found with ID {user_id}")
            return []

        # Find genres the user likes (rated >= 7.0)
        liked_genres = (
            db.query(Media.genre)
            .join(Review, Media.id == Review.media_id)
            .filter(Review.user_id == user_id, Review.rating >= 7.0)
            .distinct()
            .all()
        )
        liked_genres = [g.genre for g in liked_genres if g.genre]

        if not liked_genres:
            print(f"❌ No strong preferences found for user {user_id}. Review more media first!")
            return []

        # Find media IDs the user already reviewed
        reviewed_ids = (
            db.query(Review.media_id)
            .filter(Review.user_id == user_id)
            .all()
        )
        reviewed_ids = [r.media_id for r in reviewed_ids]

        # Recommend media in liked genres not yet reviewed
        recommendations = (
            db.query(Media)
            .filter(
                Media.genre.in_(liked_genres),
                Media.id.notin_(reviewed_ids)
            )
            .limit(5)
            .all()
        )

        if not recommendations:
            print("❌ No new recommendations found. Try reviewing more media!")
            return []

        print(f"\n💡 Recommendations for {user.name} (based on your top-rated genres):\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Genre':<15} {'Creator'}")
        print("-" * 70)
        for m in recommendations:
            print(f"{m.id:<5} {m.title:<30} {m.media_type.value:<10} "
                  f"{m.genre or 'N/A':<15} {m.creator or 'N/A'}")
        return recommendations

    finally:
        db.close()


def get_reviews_by_media(media_id: int):
    """Fetch all reviews for a specific media item."""
    db = SessionLocal()
    try:
        reviews = (
            db.query(Review)
            .filter(Review.media_id == media_id)
            .all()
        )
        return reviews
    finally:
        db.close()