from database.db import SessionLocal
from database.models import Media, MediaType


def add_media(title: str, media_type: str, genre: str, release_year: int, creator: str):
    """Add a new media item to the database."""
    db = SessionLocal()
    try:
        # Validate media_type
        try:
            mtype = MediaType(media_type.lower())
        except ValueError:
            print(f"❌ Invalid media type '{media_type}'. Choose: movie, web_show, song")
            return None

        # Check if media already exists
        existing = db.query(Media).filter(
            Media.title == title,
            Media.media_type == mtype
        ).first()
        if existing:
            print(f"❌ '{title}' already exists as a {media_type}.")
            return None

        media = Media(
            title=title,
            media_type=mtype,
            genre=genre,
            release_year=release_year,
            creator=creator
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        print(f"✅ '{title}' added successfully with ID {media.id}")
        return media

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding media: {e}")
        return None

    finally:
        db.close()


def get_all_media():
    """Fetch all media items."""
    db = SessionLocal()
    try:
        media_list = db.query(Media).all()
        if not media_list:
            print("❌ No media found.")
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
    """Search media by title (partial match)."""
    db = SessionLocal()
    try:
        results = db.query(Media).filter(Media.title.ilike(f"%{title}%")).all()
        if not results:
            print(f"❌ No media found matching '{title}'")
            return []

        print(f"\n🔍 Results for '{title}':")
        print(f"\n{'ID':<5} {'Title':<30} {'Type':<10} {'Genre':<15} {'Year':<6} {'Creator'}")
        print("-" * 75)
        for m in results:
            print(f"{m.id:<5} {m.title:<30} {m.media_type.value:<10} "
                  f"{m.genre or 'N/A':<15} {m.release_year or 'N/A':<6} {m.creator or 'N/A'}")
        return results

    finally:
        db.close()


def get_media_by_id(media_id: int):
    """Fetch a single media item by ID."""
    db = SessionLocal()
    try:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            print(f"❌ No media found with ID {media_id}")
            return None
        return media

    finally:
        db.close()