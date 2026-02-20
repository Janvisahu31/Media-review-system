import pytest
from services.media_service import add_media, get_all_media, search_by_title, get_media_by_id
from database.db import SessionLocal
from database.models import Media, Review, Favorite


def cleanup_media(title):
    db = SessionLocal()
    media = db.query(Media).filter(Media.title == title).first()
    if media:
        db.query(Review).filter(Review.media_id == media.id).delete(synchronize_session=False)
        db.query(Favorite).filter(Favorite.media_id == media.id).delete(synchronize_session=False)
        db.delete(media)
        db.commit()
    db.close()


def test_add_media_movie():
    media = add_media("Test Movie Media", "movie", "Action", 2022, "Director")
    assert media is not None
    cleanup_media("Test Movie Media")


def test_add_media_song():
    media = add_media("Test Song Media", "song", "Pop", 2021, "Artist")
    assert media is not None
    cleanup_media("Test Song Media")


def test_add_media_web_show():
    media = add_media("Test Show Media", "web_show", "Drama", 2020, "Creator")
    assert media is not None
    cleanup_media("Test Show Media")


def test_add_media_invalid_type():
    media = add_media("Test Invalid Media", "podcast", "Talk", 2022, "Host")
    assert media is None


def test_add_media_duplicate():
    add_media("Test Dupe Media", "movie", "Action", 2022, "Director")
    duplicate = add_media("Test Dupe Media", "movie", "Action", 2022, "Director")
    assert duplicate is None
    cleanup_media("Test Dupe Media")


def test_search_by_title_found(test_media):
    results = search_by_title("Test Media Fixture")
    assert len(results) > 0


def test_search_by_title_partial_match(test_media):
    results = search_by_title("Test Media")
    assert len(results) > 0


def test_search_by_title_case_insensitive(test_media):
    results = search_by_title("test media fixture")
    assert len(results) > 0


def test_search_by_title_not_found():
    results = search_by_title("xyznonexistent999abc")
    assert len(results) == 0


def test_get_media_by_id_success(test_media):
    fetched = get_media_by_id(test_media.id)
    assert fetched is not None
    assert fetched.id == test_media.id


def test_get_media_by_id_not_found():
    media = get_media_by_id(99999)
    assert media is None


def test_get_all_media_returns_list():
    results = get_all_media()
    assert isinstance(results, list)