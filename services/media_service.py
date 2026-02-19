from database.db import SessionLocal
from database.models import Media, MediaType
from patterns.factory import MediaFactory
from cache.redis_client import get_cache, set_cache, TTL_SEARCH


def add_media(title: str, media_type: str, genre: str, release_year: int, creator: str):
    """Add a new media item using the MediaFactory."""
    db = SessionLocal()
    try:
        # Factory creates and validates the media object
        media_obj = MediaFactory.create(media_type, title, genre, release_year, creator)

        # Check duplicate
        existing = db.query(Media).filter(
            Media.title == title,
            Media.media_type == media_obj.media_type
        ).first()
        if existing:
            print(f" '{title}' already exists as a {media_type}.")
            return None

        # Convert to DB model and save
        db_media = media_obj.to_db_model()
        db.add(db_media)
        db.commit()
        db.refresh(db_media)

        print(f" Added successfully!\n")
        print(media_obj.get_details())
        return db_media

    except ValueError as e:
        print(e)
        return None

    except Exception as e:
        db.rollback()
        print(f" Error adding media: {e}")
        return None

    finally:
        db.close()

def get_all_media():
    """Fetch all media items."""
    db = SessionLocal()
    try:
        media_list = db.query(Media).all()
        if not media_list:
            print("No media found.")
            return []

        print(f"\n{'ID':<5} {'Title':<30} {'Type':<10} {'Genre':<15} {'Year':<6} {'Creator'}")
        print("-" * 75)
        for m in media_list:
            print(f"{m.id:<5} {m.title:<30} {m.media_type.value:<10} "
                  f"{m.genre or 'N/A':<15} {m.release_year or 'N/A':<6} {m.creator or 'N/A'}")
        return media_list

    finally:
        db.close()


def search_by_title(title: str):
    """Search media by title — cached in Redis."""
    cache_key = f"search:{title.lower()}"

    # ── Check cache first ─────────────────────
    cached = get_cache(cache_key)
    if cached:
        print(f"\n⚡ Loaded from cache!\n")
        print(f"🔍 Results for '{title}':\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Genre':<15} {'Year':<6} {'Creator'}")
        print("-" * 75)
        for m in cached:
            print(f"{m['id']:<5} {m['title']:<30} {m['media_type']:<10} "
                  f"{m['genre']:<15} {m['release_year']:<6} {m['creator']}")
        return cached

    # ── Cache miss — query database ───────────
    db = SessionLocal()
    try:
        results = db.query(Media).filter(Media.title.ilike(f"%{title}%")).all()

        if not results:
            print(f"❌ No media found matching '{title}'")
            return []

        formatted = [
            {
                "id":           m.id,
                "title":        m.title,
                "media_type":   m.media_type.value,
                "genre":        m.genre or "N/A",
                "release_year": m.release_year or "N/A",
                "creator":      m.creator or "N/A"
            }
            for m in results
        ]

        # ── Store in Redis ─────────────────────
        set_cache(cache_key, formatted, TTL_SEARCH)

        print(f"\n🔍 Results for '{title}':\n")
        print(f"{'ID':<5} {'Title':<30} {'Type':<10} {'Genre':<15} {'Year':<6} {'Creator'}")
        print("-" * 75)
        for m in formatted:
            print(f"{m['id']:<5} {m['title']:<30} {m['media_type']:<10} "
                  f"{m['genre']:<15} {m['release_year']:<6} {m['creator']}")
        return formatted

    finally:
        db.close()


def get_media_by_id(media_id: int):
    """Fetch a single media item by ID."""
    db = SessionLocal()
    try:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            print(f" No media found with ID {media_id}")
            return None
        return media

    finally:
        db.close()