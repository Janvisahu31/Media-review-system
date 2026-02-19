import argparse
from database.db import initialize_db
from services.media_service import get_all_media, search_by_title
from services.review_service import submit_review, get_top_rated, get_recommendations
from patterns.observer import add_favorite, get_notifications
from utils.auth import login, logout, get_current_user, login_required




def handle_list(args):
    get_all_media()


def handle_search(args):
    search_by_title(args.search)


def handle_top_rated(args):
    get_top_rated()


def handle_login(args):
    login(args.login[0], args.login[1])


def handle_logout(args):
    logout()


@login_required
def handle_review(args, user):
    submit_review(user["user_id"], args.review[0], float(args.review[1]), args.review[2])


@login_required
def handle_bulk_review(args, user):
    print(f"📂 Bulk review from '{args.bulk_review}' — coming soon!")


@login_required
def handle_recommend(args, user):
    get_recommendations(user["user_id"])


@login_required
def handle_favorite(args, user):
    add_favorite(user["user_id"], int(args.favorite))


@login_required
def handle_notification(args, user):
    get_notifications(user["user_id"])



def main():
    parser = argparse.ArgumentParser(description="🎬 Media Review CLI System")

    parser.add_argument("--list",      action="store_true", help="List all media")
    parser.add_argument("--top-rated", action="store_true", help="Get top rated media")
    parser.add_argument("--search",    type=str,            metavar="TITLE",
                        help="Search media by title")

    parser.add_argument("--login",  nargs=2, metavar=("EMAIL", "PASSWORD"),
                        help="Login: --login <email> <password>")
    parser.add_argument("--logout", action="store_true",
                        help="Logout current user")

    parser.add_argument("--review", nargs=3,
                        metavar=("MEDIA_ID", "RATING", "COMMENT"),
                        help="Submit a review (must be logged in)")
    parser.add_argument("--bulk-review", type=str, metavar="FILE",
                        help="Bulk submit reviews from CSV (must be logged in)")
    parser.add_argument("--recommend",   action="store_true",
                        help="Get recommendations (must be logged in)")
    parser.add_argument("--favorite",    type=int, metavar="MEDIA_ID",
                        help="Favorite a media item (must be logged in)")
    parser.add_argument("--notification", action="store_true",
                        help="Check notifications (must be logged in)")

    args = parser.parse_args()
    initialize_db()

    if args.list:
        handle_list(args)
    elif args.search:
        handle_search(args)
    elif args.top_rated:
        handle_top_rated(args)
    elif args.login:
        handle_login(args)
    elif args.logout:
        handle_logout(args)
    elif args.review:
        handle_review(args)
    elif args.bulk_review:
        handle_bulk_review(args)
    elif args.recommend:
        handle_recommend(args)
    elif args.favorite:
        handle_favorite(args)
    elif args.notification:
        handle_notification(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()