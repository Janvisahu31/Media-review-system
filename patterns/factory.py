from database.models import Media, MediaType


# ──────────────────────────────────────────────
# Base class
# ──────────────────────────────────────────────

class BaseMedia:
    """Base class that all media types inherit from."""

    def __init__(self, title: str, genre: str, release_year: int, creator: str):
        self.title        = title
        self.genre        = genre
        self.release_year = release_year
        self.creator      = creator

    def get_details(self):
        raise NotImplementedError("Each media type must implement get_details()")

    def to_db_model(self):
        raise NotImplementedError("Each media type must implement to_db_model()")


# ──────────────────────────────────────────────
# Concrete media types
# ──────────────────────────────────────────────

class Movie(BaseMedia):
    """Represents a Movie."""

    media_type = MediaType.MOVIE

    def get_details(self):
        return (
            f" Movie     : {self.title}\n"
            f"   Director  : {self.creator}\n"
            f"   Genre     : {self.genre}\n"
            f"   Released  : {self.release_year}"
        )

    def to_db_model(self):
        return Media(
            title=self.title,
            media_type=self.media_type,
            genre=self.genre,
            release_year=self.release_year,
            creator=self.creator
        )


class WebShow(BaseMedia):
    """Represents a Web Show / Series."""

    media_type = MediaType.WEB_SHOW

    def get_details(self):
        return (
            f"Web Show  : {self.title}\n"
            f"   Creator   : {self.creator}\n"
            f"   Genre     : {self.genre}\n"
            f"   Released  : {self.release_year}"
        )

    def to_db_model(self):
        return Media(
            title=self.title,
            media_type=self.media_type,
            genre=self.genre,
            release_year=self.release_year,
            creator=self.creator
        )


class Song(BaseMedia):
    """Represents a Song."""

    media_type = MediaType.SONG

    def get_details(self):
        return (
            f" Song      : {self.title}\n"
            f"   Artist    : {self.creator}\n"
            f"   Genre     : {self.genre}\n"
            f"   Released  : {self.release_year}"
        )

    def to_db_model(self):
        return Media(
            title=self.title,
            media_type=self.media_type,
            genre=self.genre,
            release_year=self.release_year,
            creator=self.creator
        )


# ──────────────────────────────────────────────
# The Factory
# ──────────────────────────────────────────────

class MediaFactory:
    """
    Factory class that creates the correct media object
    based on the media_type string provided.
    """

    _creators = {
        "movie":    Movie,
        "web_show": WebShow,
        "song":     Song,
    }

    @staticmethod
    def create(media_type: str, title: str, genre: str, release_year: int, creator: str):
        """
        Create and return the correct media object.
        
        Args:
            media_type   : one of 'movie', 'web_show', 'song'
            title        : title of the media
            genre        : genre of the media
            release_year : year of release
            creator      : director for movies/shows, artist for songs

        Returns:
            Movie | WebShow | Song instance
        """
        media_class = MediaFactory._creators.get(media_type.lower())

        if not media_class:
            valid = list(MediaFactory._creators.keys())
            raise ValueError(f" Invalid media type '{media_type}'. Choose from: {valid}")

        return media_class(
            title=title,
            genre=genre,
            release_year=release_year,
            creator=creator
        )

    @staticmethod
    def supported_types():
        return list(MediaFactory._creators.keys())