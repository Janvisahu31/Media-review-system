# from database.db import get_connection, initialize_db

# def add_user():
#     username = input("Enter username: ")
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
#     conn.commit()
#     conn.close()
#     print("User added successfully!")

# def add_media():
#     title = input("Enter media title: ")
#     media_type = input("Enter type (movie/webshow/song): ")
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO media (title, type) VALUES (?, ?)", (title, media_type))
#     conn.commit()
#     conn.close()
#     print("Media added successfully!")

# def add_review():
#     user_id = int(input("Enter user id: "))
#     media_id = int(input("Enter media id: "))
#     rating = int(input("Enter rating (1-5): "))
#     review_text = input("Enter review: ")

#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO reviews (user_id, media_id, rating, review_text)
#         VALUES (?, ?, ?, ?)
#     """, (user_id, media_id, rating, review_text))
#     conn.commit()
#     conn.close()
#     print("Review added!")

# def view_reviews():
#     media_id = int(input("Enter media id: "))
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT users.username, reviews.rating, reviews.review_text
#         FROM reviews
#         JOIN users ON users.id = reviews.user_id
#         WHERE reviews.media_id = ?
#     """, (media_id,))
    
#     results = cursor.fetchall()
#     for row in results:
#         print(f"User: {row[0]} | Rating: {row[1]} | Review: {row[2]}")
    
#     conn.close()

# def menu():
#     while True:
#         print("\n1. Add User")
#         print("2. Add Media")
#         print("3. Add Review")
#         print("4. View Reviews")
#         print("5. Exit")

#         choice = input("Choose option: ")

#         if choice == "1":
#             add_user()
#         elif choice == "2":
#             add_media()
#         elif choice == "3":
#             add_review()
#         elif choice == "4":
#             view_reviews()
#         elif choice == "5":
#             break
#         else:
#             print("Invalid choice")

# if __name__ == "__main__":
#     initialize_db()
#     menu()


import argparse
from database.db import initialize_db

def main():
    parser = argparse.ArgumentParser(description="Media Review CLI System")

    parser.add_argument("--list", action="store_true", help="List all media")
    parser.add_argument("--review", nargs=3, metavar=("media_id", "rating", "comment"))
    parser.add_argument("--bulk-review", type=str, help="Add multiple reviews from file")
    parser.add_argument("--search", type=str, help="Search media by title")
    parser.add_argument("--top-rated", action="store_true")
    parser.add_argument("--recommend", type=int, help="Recommend for user_id")
    parser.add_argument("--notification", type=int, help="Get notifications for media_id")

    args = parser.parse_args()

    initialize_db()

    if args.list:
        list_media()

    elif args.review:
        media_id, rating, comment = args.review
        add_review(int(media_id), int(rating), comment)

    elif args.bulk_review:
        bulk_review(args.bulk_review)

    elif args.search:
        search_media(args.search)

    elif args.top_rated:
        top_rated()

    elif args.recommend:
        recommend(args.recommend)

    elif args.notification:
        get_notifications(args.notification)

    else:
        parser.print_help()


if __name__ == "__main__":
    initialize_db()
    print("✅ Database initialized successfully")
