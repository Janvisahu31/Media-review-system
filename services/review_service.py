from database.db import SessionLocal
from database.models import Review, Media, User
from sqlalchemy import func
import threading
import csv
import time
from cache.redis_client import get_cache, set_cache, delete_cache, TTL_TOP_RATED

db_lock = threading.Lock()


def submit_review(user_id: int, media_id: int, rating: float, comment: str):
    """Submit a single review."""
    db = SessionLocal()
    try:
        # Validate rating
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

        # Check duplicate
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
        print(f"✅ Review submitted for '{media.title}' by {user.name} | Rating: {rating}/10")

        # Invalidate top-rated cache since ratings changed
        delete_cache("top_rated:5")

        return review

    except Exception as e:
        db.rollback()
        print(f"❌ Error submitting review: {e}")
        return None

    finally:
        db.close()


def submit_review_thread(user_id: int, media_id: int, rating: float,
                          comment: str, results: list, index: int):
    """Thread-safe version of submit_review."""
    db = SessionLocal()
    try:
        if not (1.0 <= rating <= 10.0):
            results[index] = f"❌ Row {index+1}: Rating must be between 1.0 and 10.0"
            return

        user  = db.query(User).filter(User.id == user_id).first()
        media = db.query(Media).filter(Media.id == media_id).first()

        if not user:
            results[index] = f"❌ Row {index+1}: No user found with ID {user_id}"
            return
        if not media:
            results[index] = f"❌ Row {index+1}: No media found with ID {media_id}"
            return

        existing = db.query(Review).filter(
            Review.user_id == user_id,
            Review.media_id == media_id
        ).first()
        if existing:
            results[index] = f"❌ Row {index+1}: User {user_id} already reviewed '{media.title}'"
            return

        with db_lock:
            review = Review(
                user_id=user_id,
                media_id=media_id,
                rating=rating,
                comment=comment
            )
            db.add(review)
            db.commit()
            results[index] = f"✅ Row {index+1}: Review submitted for '{media.title}' | Rating: {rating}/10"

    except Exception as e:
        db.rollback()
        results[index] = f"❌ Row {index+1}: Error — {e}"

    finally:
        db.close()


def bulk_submit_reviews(file_path: str, user_id: int):
    """Read reviews from CSV and submit concurrently using multithreading.
    
    CSV format:
        media_id, rating, comment
    """
    reviews = []

    try:
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    reviews.append({
                        "media_id": int(row["media_id"].strip()),
                        "rating":   float(row["rating"].strip()),
                        "comment":  row["comment"].strip()
                    })
                except (ValueError, KeyError) as e:
                    print(f"⚠️  Skipping invalid row: {row} — {e}")

    except FileNotFoundError:
        print(f"❌ File '{file_path}' not found.")
        return

    if not reviews:
        print("❌ No valid reviews found in file.")
        return

    print(f"\n📂 Found {len(reviews)} reviews in '{file_path}'")
    print(f"🚀 Submitting concurrently using {len(reviews)} threads...\n")

    results = [None] * len(reviews)
    threads = []

    # ── Start timer ───────────────────────────
    start_time = time.perf_counter()

    for i, review in enumerate(reviews):
        thread = threading.Thread(
            target=submit_review_thread,
            args=(
                user_id,
                review["media_id"],
                review["rating"],
                review["comment"],
                results,
                i
            )
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # ── Stop timer ────────────────────────────
    end_time = time.perf_counter()
    elapsed  = end_time - start_time

    # ── Print results ─────────────────────────
    print("📋 Bulk Review Results:\n")
    success = 0
    failed  = 0
    for result in results:
        print(result)
        if result.startswith("✅"):
            success += 1
        else:
            failed += 1

    print(f"\n{'─'*40}")
    print(f"✅ Successful : {success}")
    print(f"❌ Failed     : {failed}")
    print(f"📊 Total      : {len(reviews)}")
    print(f"⏱️  Time taken : {elapsed:.4f} seconds")
    print(f"⚡ Avg/review : {(elapsed/len(reviews)*1000):.2f} ms")
    print(f"{'─'*40}")


def get_top_rated(limit: int = 5):
    """Get top rated media — cached in Redis."""
    cache_key = f"top_rated:{limit}"

    # ── Check cache first ─────────────────────
    cached = get_cache(cache_key)
    if cached:
        print(f"\n⚡ Loaded from cache!\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Avg Rating':<12} {'Reviews'}")
        print("-" * 65)
        for r in cached:
            print(f"{r['id']:<5} {r['title']:<30} {r['media_type']:<10} "
                  f"{r['avg_rating']:<12} {r['review_count']}")
        return cached
     # ── Cache miss — query database ───────────
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

        # ── Format for display and cache ──────
        formatted = [
            {
                "id":           r.id,
                "title":        r.title,
                "media_type":   r.media_type.value,
                "genre":        r.genre,
                "avg_rating":   round(r.avg_rating, 2),
                "review_count": r.review_count
            }
            for r in results
        ]

         # ── Store in Redis ─────────────────────
        set_cache(cache_key, formatted, TTL_TOP_RATED)

        print(f"\n⭐ Top {limit} Rated Media:\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Avg Rating':<12} {'Reviews'}")
        print("-" * 65)
        for r in formatted:
            print(f"{r['id']:<5} {r['title']:<30} {r['media_type']:<10} "
                  f"{r['avg_rating']:<12} {r['review_count']}")
        return formatted

    finally:
        db.close()


def get_recommendations(user_id: int):
    """Recommend media based on genres user rated >= 7.0."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ No user found with ID {user_id}")
            return []

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

        reviewed_ids = (
            db.query(Review.media_id)
            .filter(Review.user_id == user_id)
            .all()
        )
        reviewed_ids = [r.media_id for r in reviewed_ids]

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
        return db.query(Review).filter(Review.media_id == media_id).all()
    finally:
        db.close()