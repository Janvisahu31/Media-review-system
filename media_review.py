import argparse
from database.db import initialize_db
from services.media_service import get_all_media, search_by_title
from services.review_service import submit_review, get_top_rated, get_recommendations


def main():
    parser = argparse.ArgumentParser(description="🎬 Media Review CLI System")

    parser.add_argument("--list",         action="store_true",  help="List all media")
    parser.add_argument("--top-rated",    action="store_true",  help="Get top rated media")
    parser.add_argument("--search",       type=str,             metavar="TITLE",
                        help="Search media by title")
    parser.add_argument("--recommend",    type=int,             metavar="USER_ID",
                        help="Get recommendations for a user")
    parser.add_argument("--notification", type=int,             metavar="MEDIA_ID",
                        help="Get notifications for a media item")
    parser.add_argument("--bulk-review",  type=str,             metavar="FILE",
                        help="Bulk submit reviews from a CSV file")
    parser.add_argument(
        "--review",
        nargs=4,
        metavar=("USER_ID", "MEDIA_ID", "RATING", "COMMENT"),
        help="Submit a review: --review <user_id> <media_id> <rating> <comment>"
    )

    args = parser.parse_args()
    initialize_db()

    if args.list:
        get_all_media()

    elif args.review:
        user_id, media_id, rating, comment = args.review
        submit_review(int(user_id), int(media_id), float(rating), comment)

    elif args.search:
        search_by_title(args.search)

    elif args.top_rated:
        get_top_rated()

    elif args.recommend:
        get_recommendations(args.recommend)

    elif args.notification:
        print(f"🔔 Notifications for media {args.notification} — coming soon!")

    elif args.bulk_review:
        print(f"📂 Bulk review from '{args.bulk_review}' — coming soon!")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()