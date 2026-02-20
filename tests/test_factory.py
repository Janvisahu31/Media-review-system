import pytest
from patterns.factory import MediaFactory, Movie, WebShow, Song
from database.models import MediaType


def test_factory_creates_movie():
    media = MediaFactory.create("movie", "Test Movie", "Action", 2022, "Director")
    assert isinstance(media, Movie)
    assert media.media_type == MediaType.MOVIE


def test_factory_creates_webshow():
    media = MediaFactory.create("web_show", "Test Show", "Drama", 2021, "Creator")
    assert isinstance(media, WebShow)
    assert media.media_type == MediaType.WEB_SHOW


def test_factory_creates_song():
    media = MediaFactory.create("song", "Test Song", "Pop", 2020, "Artist")
    assert isinstance(media, Song)
    assert media.media_type == MediaType.SONG


def test_factory_invalid_type():
    with pytest.raises(ValueError):
        MediaFactory.create("podcast", "Test", "Talk", 2022, "Host")


def test_factory_case_insensitive_movie():
    media = MediaFactory.create("MOVIE", "Test", "Action", 2022, "Director")
    assert isinstance(media, Movie)


def test_factory_case_insensitive_song():
    media = MediaFactory.create("SONG", "Test", "Pop", 2022, "Artist")
    assert isinstance(media, Song)


def test_factory_supported_types():
    types = MediaFactory.supported_types()
    assert "movie"    in types
    assert "web_show" in types
    assert "song"     in types
    assert len(types) == 3


def test_movie_get_details():
    movie   = MediaFactory.create("movie", "Inception", "Sci-Fi", 2010, "Nolan")
    details = movie.get_details()
    assert "Inception" in details
    assert "Nolan"     in details
    assert "Movie"        in details


def test_webshow_get_details():
    show    = MediaFactory.create("web_show", "Breaking Bad", "Drama", 2008, "Gilligan")
    details = show.get_details()
    assert "Breaking Bad" in details
    assert "Gilligan"     in details
    assert "Web Show"           in details


def test_song_get_details():
    song    = MediaFactory.create("song", "Starboy", "R&B", 2016, "The Weeknd")
    details = song.get_details()
    assert "Starboy"    in details
    assert "The Weeknd" in details
    assert "Song"      in details


def test_movie_to_db_model():
    movie    = MediaFactory.create("movie", "Test", "Action", 2022, "Director")
    db_model = movie.to_db_model()
    assert db_model.title      == "Test"
    assert db_model.media_type == MediaType.MOVIE
    assert db_model.genre      == "Action"
    assert db_model.creator    == "Director"


def test_song_to_db_model():
    song     = MediaFactory.create("song", "Test Song", "Pop", 2021, "Artist")
    db_model = song.to_db_model()
    assert db_model.title      == "Test Song"
    assert db_model.media_type == MediaType.SONG


def test_webshow_to_db_model():
    show     = MediaFactory.create("web_show", "Test Show", "Drama", 2020, "Creator")
    db_model = show.to_db_model()
    assert db_model.title      == "Test Show"
    assert db_model.media_type == MediaType.WEB_SHOW