import argparse
from database.db import initialize_db
from services.media_service import get_all_media, search_by_title
from services.review_service import submit_review, get_top_rated, get_recommendations, bulk_submit_reviews
from patterns.observer import add_favorite, get_notifications
from utils.auth import login, logout, get_current_user, login_required, register, change_password, cleanup_sessions




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
    bulk_submit_reviews(args.bulk_review, user["user_id"])


@login_required
def handle_recommend(args, user):
    get_recommendations(user["user_id"])


@login_required
def handle_favorite(args, user):
    add_favorite(user["user_id"], int(args.favorite))


@login_required
def handle_notification(args, user):
    last_seen = user.get("last_seen")
    if not last_seen:
        print("❌ Session missing last_seen. Please login again.")
        return
    get_notifications(user["user_id"],last_seen)

def handle_register(args):
    name, email, password = args.register
    register(name, email, password)

@login_required
def handle_change_password(args, user):
    old_password, new_password = args.change_password
    change_password(user["user_id"], old_password, new_password)


def handle_whoami(args):
    user = get_current_user()
    if user:
        print(f"\n👤 Logged in as: {user['name']}")
        print(f"   Email       : {user['email']}")
        print(f"   User ID     : {user['user_id']}")
    else:
        print("❌ Not logged in.")
        print("   Run: python media_review.py --login <email> <password>")
    
def handle_sessions(args):
    import glob
    import json
    import platform

    session_files = glob.glob(".session_*.json")

    if not session_files:
        print("❌ No active sessions found.")
        return

    print(f"\n{'─'*55}")
    print(f"  Active Sessions ({len(session_files)} terminal(s))")
    print(f"{'─'*55}")
    print(f"{'Terminal ID':<15} {'User':<15} {'Email':<25}")
    print(f"{'─'*55}")

    for session_file in session_files:
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
            terminal_id = session_file.replace(".session_", "").replace(".json", "")
            current     = "← YOU" if terminal_id == os.environ.get("MEDIA_TERMINAL_ID", "") else ""
            print(f"{terminal_id:<15} {data.get('name','?'):<15} {data.get('email','?'):<25} {current}")
        except Exception:
            print(f"  {session_file} — unreadable")

    print(f"{'─'*55}\n")


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
    parser.add_argument("--sessions", action="store_true", help="List all active terminal sessions")
    

    parser.add_argument(
    "--register",
    nargs=3,
    metavar=("NAME", "EMAIL", "PASSWORD"),
    help="Register a new account"
    )

    parser.add_argument(
        "--change-password",
        nargs=2,
        metavar=("OLD_PASSWORD", "NEW_PASSWORD"),
        help="Change your password (must be logged in)"
    )
    parser.add_argument(
        "--whoami",
        action="store_true",
        help="Show currently logged in user"
    )

    args = parser.parse_args()
    initialize_db()
    cleanup_sessions()

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

    elif args.register:
        handle_register(args)

    elif args.whoami:
        handle_whoami(args)

    elif args.change_password:
        handle_change_password(args)
    elif args.sessions:
        handle_sessions(args)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()





