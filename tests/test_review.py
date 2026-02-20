import pytest
from services.review_service import (
    submit_review, get_top_rated,
    get_recommendations, get_reviews_by_media
)


def test_submit_review_success(test_user, test_media):
    review = submit_review(test_user.id, test_media.id, 8.5, "Great!")
    assert review is not None
    assert review.rating  == 8.5
    assert review.user_id == test_user.id


def test_submit_review_rating_too_high(test_user, test_media):
    review = submit_review(test_user.id, test_media.id, 11.0, "Too high")
    assert review is None


def test_submit_review_rating_too_low(test_user, test_media):
    review = submit_review(test_user.id, test_media.id, 0.0, "Too low")
    assert review is None


def test_submit_review_boundary_low(test_user, test_media):
    """Rating of exactly 1.0 should be valid."""
    review = submit_review(test_user.id, test_media.id, 1.0, "Minimum rating")
    assert review is not None


def test_submit_review_boundary_high(test_user, test_media_2):
    """Rating of exactly 10.0 should be valid."""
    review = submit_review(test_user.id, test_media_2.id, 10.0, "Maximum rating")
    assert review is not None


def test_submit_review_duplicate(test_user, test_media):
    submit_review(test_user.id, test_media.id, 8.5, "First review")
    duplicate = submit_review(test_user.id, test_media.id, 7.0, "Second review")
    assert duplicate is None


def test_submit_review_invalid_user(test_media):
    review = submit_review(99999, test_media.id, 8.0, "Ghost user")
    assert review is None


def test_submit_review_invalid_media(test_user):
    review = submit_review(test_user.id, 99999, 8.0, "Ghost media")
    assert review is None


def test_get_top_rated_returns_list():
    results = get_top_rated()
    assert isinstance(results, list)


def test_get_top_rated_limit(test_user, test_media):
    submit_review(test_user.id, test_media.id, 9.0, "Good")
    results = get_top_rated(limit=3)
    assert len(results) <= 3


def test_get_recommendations_invalid_user():
    results = get_recommendations(99999)
    assert results == []


def test_get_reviews_by_media(test_review, test_media):
    reviews = get_reviews_by_media(test_media.id)
    assert isinstance(reviews, list)
    assert len(reviews) > 0


def test_get_reviews_by_media_no_reviews():
    reviews = get_reviews_by_media(99999)
    assert reviews == []