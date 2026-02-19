from database.db import initialize_db, SessionLocal
from database.models import User, Media, MediaType, Review, Favorite
from services.user_service import add_user
from services.media_service import add_media
from services.review_service import submit_review
from patterns.observer import add_favorite


def user_exists(email: str) -> bool:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first() is not None
    finally:
        db.close()


def media_exists(title: str, media_type: str) -> bool:
    db = SessionLocal()
    try:
        mtype = MediaType(media_type.lower())
        return db.query(Media).filter(
            Media.title == title,
            Media.media_type == mtype
        ).first() is not None
    finally:
        db.close()


def review_exists(user_id: int, media_id: int) -> bool:
    db = SessionLocal()
    try:
        return db.query(Review).filter(
            Review.user_id == user_id,
            Review.media_id == media_id
        ).first() is not None
    finally:
        db.close()


def favorite_exists(user_id: int, media_id: int) -> bool:
    db = SessionLocal()
    try:
        return db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.media_id == media_id
        ).first() is not None
    finally:
        db.close()


def get_user_id(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.id if user else None
    finally:
        db.close()


def get_media_id(title: str, media_type: str):
    db = SessionLocal()
    try:
        mtype = MediaType(media_type.lower())
        media = db.query(Media).filter(
            Media.title == title,
            Media.media_type == mtype
        ).first()
        return media.id if media else None
    finally:
        db.close()


def safe_add_user(name, email, password):
    if user_exists(email):
        print(f"⏭️  Skipping user '{name}' — already exists")
        return get_user_id(email)
    add_user(name, email, password)
    return get_user_id(email)


def safe_add_media(title, media_type, genre, release_year, creator):
    if media_exists(title, media_type):
        print(f"⏭️  Skipping media '{title}' — already exists")
        return get_media_id(title, media_type)
    add_media(title, media_type, genre, release_year, creator)
    return get_media_id(title, media_type)


def safe_add_review(user_id, media_id, rating, comment):
    if review_exists(user_id, media_id):
        print(f"⏭️  Skipping review — user {user_id} already reviewed media {media_id}")
        return
    submit_review(user_id, media_id, rating, comment)


def safe_add_favorite(user_id, media_id):
    if favorite_exists(user_id, media_id):
        print(f"⏭️  Skipping favorite — already exists")
        return
    add_favorite(user_id, media_id)


def seed():
    print("🌱 Seeding database — skipping existing data...\n")
    initialize_db()

    # ──────────────────────────────────────────────
    # 50 Users
    # ──────────────────────────────────────────────
    print("👤 Adding 50 users...")
    users_data = [
        ("Alice",      "alice@example.com",      "pass123"),
        ("Bob",        "bob@example.com",         "pass456"),
        ("Janvi",      "janvi@example.com",       "pass789"),
        ("Nitish",     "nitish@example.com",      "pass000"),
        ("Charlie",    "charlie@example.com",     "pass111"),
        ("Diana",      "diana@example.com",       "pass222"),
        ("Ethan",      "ethan@example.com",       "pass333"),
        ("Fiona",      "fiona@example.com",       "pass444"),
        ("George",     "george@example.com",      "pass555"),
        ("Hannah",     "hannah@example.com",      "pass666"),
        ("Ivan",       "ivan@example.com",        "pass101"),
        ("Julia",      "julia@example.com",       "pass102"),
        ("Kevin",      "kevin@example.com",       "pass103"),
        ("Laura",      "laura@example.com",       "pass104"),
        ("Mike",       "mike@example.com",        "pass105"),
        ("Nina",       "nina@example.com",        "pass106"),
        ("Oscar",      "oscar@example.com",       "pass107"),
        ("Priya",      "priya@example.com",       "pass108"),
        ("Quinn",      "quinn@example.com",       "pass109"),
        ("Rachel",     "rachel@example.com",      "pass110"),
        ("Sam",        "sam@example.com",         "pass111"),
        ("Tina",       "tina@example.com",        "pass112"),
        ("Uma",        "uma@example.com",         "pass113"),
        ("Victor",     "victor@example.com",      "pass114"),
        ("Wendy",      "wendy@example.com",       "pass115"),
        ("Xander",     "xander@example.com",      "pass116"),
        ("Yara",       "yara@example.com",        "pass117"),
        ("Zoe",        "zoe@example.com",         "pass118"),
        ("Aaron",      "aaron@example.com",       "pass119"),
        ("Bella",      "bella@example.com",       "pass120"),
        ("Carlos",     "carlos@example.com",      "pass121"),
        ("Daisy",      "daisy@example.com",       "pass122"),
        ("Elliot",     "elliot@example.com",      "pass123"),
        ("Faith",      "faith@example.com",       "pass124"),
        ("Gavin",      "gavin@example.com",       "pass125"),
        ("Heidi",      "heidi@example.com",       "pass126"),
        ("Ian",        "ian@example.com",         "pass127"),
        ("Jasmine",    "jasmine@example.com",     "pass128"),
        ("Kyle",       "kyle@example.com",        "pass129"),
        ("Lily",       "lily@example.com",        "pass130"),
        ("Mason",      "mason@example.com",       "pass131"),
        ("Nora",       "nora@example.com",        "pass132"),
        ("Owen",       "owen@example.com",        "pass133"),
        ("Paige",      "paige@example.com",       "pass134"),
        ("Rohan",      "rohan@example.com",       "pass135"),
        ("Sophie",     "sophie@example.com",      "pass136"),
        ("Tyler",      "tyler@example.com",       "pass137"),
        ("Ursula",     "ursula@example.com",      "pass138"),
        ("Vivian",     "vivian@example.com",      "pass139"),
        ("Walter",     "walter@example.com",      "pass140"),
    ]
    user_ids = [safe_add_user(n, e, p) for n, e, p in users_data]

    # ──────────────────────────────────────────────
    # 50 Movies
    # ──────────────────────────────────────────────
    print("\n🎬 Adding 50 movies...")
    movies_data = [
        ("Inception",                "Sci-Fi",   2010, "Christopher Nolan"),
        ("The Dark Knight",          "Action",   2008, "Christopher Nolan"),
        ("Interstellar",             "Sci-Fi",   2014, "Christopher Nolan"),
        ("The Godfather",            "Drama",    1972, "Francis Ford Coppola"),
        ("Parasite",                 "Thriller", 2019, "Bong Joon-ho"),
        ("Pulp Fiction",             "Crime",    1994, "Quentin Tarantino"),
        ("The Shawshank Redemption", "Drama",    1994, "Frank Darabont"),
        ("Fight Club",               "Drama",    1999, "David Fincher"),
        ("Forrest Gump",             "Drama",    1994, "Robert Zemeckis"),
        ("The Matrix",               "Sci-Fi",   1999, "The Wachowskis"),
        ("Goodfellas",               "Crime",    1990, "Martin Scorsese"),
        ("Schindler's List",         "Drama",    1993, "Steven Spielberg"),
        ("The Silence of the Lambs", "Thriller", 1991, "Jonathan Demme"),
        ("Gladiator",                "Action",   2000, "Ridley Scott"),
        ("The Lion King",            "Animation",1994, "Roger Allers"),
        ("Avengers Endgame",         "Action",   2019, "Russo Brothers"),
        ("Titanic",                  "Romance",  1997, "James Cameron"),
        ("Avatar",                   "Sci-Fi",   2009, "James Cameron"),
        ("The Prestige",             "Mystery",  2006, "Christopher Nolan"),
        ("Memento",                  "Mystery",  2000, "Christopher Nolan"),
        ("1917",                     "War",      2019, "Sam Mendes"),
        ("Joker",                    "Drama",    2019, "Todd Phillips"),
        ("The Revenant",             "Adventure",2015, "Alejandro Inarritu"),
        ("Mad Max Fury Road",        "Action",   2015, "George Miller"),
        ("Her",                      "Sci-Fi",   2013, "Spike Jonze"),
        ("Django Unchained",         "Western",  2012, "Quentin Tarantino"),
        ("The Grand Budapest Hotel", "Comedy",   2014, "Wes Anderson"),
        ("La La Land",               "Romance",  2016, "Damien Chazelle"),
        ("Whiplash",                 "Drama",    2014, "Damien Chazelle"),
        ("Gone Girl",                "Thriller", 2014, "David Fincher"),
        ("No Country for Old Men",   "Thriller", 2007, "Coen Brothers"),
        ("There Will Be Blood",      "Drama",    2007, "Paul Thomas Anderson"),
        ("Eternal Sunshine",         "Romance",  2004, "Michel Gondry"),
        ("Oldboy",                   "Thriller", 2003, "Park Chan-wook"),
        ("City of God",              "Crime",    2002, "Fernando Meirelles"),
        ("Pan's Labyrinth",          "Fantasy",  2006, "Guillermo del Toro"),
        ("Spirited Away",            "Animation",2001, "Hayao Miyazaki"),
        ("Princess Mononoke",        "Animation",1997, "Hayao Miyazaki"),
        ("Blade Runner 2049",        "Sci-Fi",   2017, "Denis Villeneuve"),
        ("Arrival",                  "Sci-Fi",   2016, "Denis Villeneuve"),
        ("Dune",                     "Sci-Fi",   2021, "Denis Villeneuve"),
        ("The Batman",               "Action",   2022, "Matt Reeves"),
        ("Everything Everywhere",    "Sci-Fi",   2022, "Daniels"),
        ("Tár",                      "Drama",    2022, "Todd Field"),
        ("Oppenheimer",              "Drama",    2023, "Christopher Nolan"),
        ("Barbie",                   "Comedy",   2023, "Greta Gerwig"),
        ("Poor Things",              "Fantasy",  2023, "Yorgos Lanthimos"),
        ("The Zone of Interest",     "Drama",    2023, "Jonathan Glazer"),
        ("Past Lives",               "Romance",  2023, "Celine Song"),
        ("Killers of the Flower Moon","Drama",   2023, "Martin Scorsese"),
    ]
    movie_ids = [safe_add_media(t, "movie", g, y, c) for t, g, y, c in movies_data]

    # ──────────────────────────────────────────────
    # 50 Web Shows
    # ──────────────────────────────────────────────
    print("\n📺 Adding 50 web shows...")
    shows_data = [
        ("Breaking Bad",          "Drama",   2008, "Vince Gilligan"),
        ("Stranger Things",       "Sci-Fi",  2016, "The Duffer Brothers"),
        ("The Crown",             "Drama",   2016, "Peter Morgan"),
        ("Dark",                  "Sci-Fi",  2017, "Baran bo Odar"),
        ("Chernobyl",             "Drama",   2019, "Craig Mazin"),
        ("Game of Thrones",       "Fantasy", 2011, "Benioff and Weiss"),
        ("The Wire",              "Crime",   2002, "David Simon"),
        ("Sopranos",              "Crime",   1999, "David Chase"),
        ("True Detective",        "Thriller",2014, "Nic Pizzolatto"),
        ("Mindhunter",            "Thriller",2017, "David Fincher"),
        ("Black Mirror",          "Sci-Fi",  2011, "Charlie Brooker"),
        ("Westworld",             "Sci-Fi",  2016, "Nolan and Joy"),
        ("Succession",            "Drama",   2018, "Jesse Armstrong"),
        ("The Boys",              "Action",  2019, "Eric Kripke"),
        ("Peaky Blinders",        "Crime",   2013, "Steven Knight"),
        ("Better Call Saul",      "Drama",   2015, "Vince Gilligan"),
        ("Narcos",                "Crime",   2015, "Chris Brancato"),
        ("Ozark",                 "Thriller",2017, "Bill Dubuque"),
        ("Squid Game",            "Thriller",2021, "Hwang Dong-hyuk"),
        ("Money Heist",           "Crime",   2017, "Alex Pina"),
        ("The Last of Us",        "Drama",   2023, "Craig Mazin"),
        ("House of Dragon",       "Fantasy", 2022, "Ryan Condal"),
        ("Andor",                 "Sci-Fi",  2022, "Tony Gilroy"),
        ("Severance",             "Sci-Fi",  2022, "Dan Erickson"),
        ("The Bear",              "Drama",   2022, "Christopher Storer"),
        ("Abbott Elementary",     "Comedy",  2021, "Quinta Brunson"),
        ("Ted Lasso",             "Comedy",  2020, "Jason Sudeikis"),
        ("Fleabag",               "Comedy",  2016, "Phoebe Waller-Bridge"),
        ("Killing Eve",           "Thriller",2018, "Phoebe Waller-Bridge"),
        ("Sharp Objects",         "Thriller",2018, "Jean-Marc Vallee"),
        ("Big Little Lies",       "Drama",   2017, "Jean-Marc Vallee"),
        ("Mare of Easttown",      "Thriller",2021, "Brad Ingelsby"),
        ("The White Lotus",       "Drama",   2021, "Mike White"),
        ("Euphoria",              "Drama",   2019, "Sam Levinson"),
        ("Atlanta",               "Comedy",  2016, "Donald Glover"),
        ("Barry",                 "Comedy",  2018, "Bill Hader"),
        ("Silicon Valley",        "Comedy",  2014, "Mike Judge"),
        ("Arrested Development",  "Comedy",  2003, "Mitchell Hurwitz"),
        ("The Office",            "Comedy",  2005, "Greg Daniels"),
        ("Parks and Recreation",  "Comedy",  2009, "Greg Daniels"),
        ("Fargo",                 "Crime",   2014, "Noah Hawley"),
        ("Hannibal",              "Thriller",2013, "Bryan Fuller"),
        ("Mr Robot",              "Thriller",2015, "Sam Esmail"),
        ("Halt and Catch Fire",   "Drama",   2014, "Christopher Cantwell"),
        ("Band of Brothers",      "War",     2001, "Steven Spielberg"),
        ("The Pacific",           "War",     2010, "Steven Spielberg"),
        ("Rome",                  "Drama",   2005, "Bruno Heller"),
        ("Deadwood",              "Western", 2004, "David Milch"),
        ("Boardwalk Empire",      "Crime",   2010, "Terence Winter"),
        ("Justified",             "Crime",   2010, "Graham Yost"),
    ]
    show_ids = [safe_add_media(t, "web_show", g, y, c) for t, g, y, c in shows_data]

    # ──────────────────────────────────────────────
    # 50 Songs
    # ──────────────────────────────────────────────
    print("\n🎵 Adding 50 songs...")
    songs_data = [
        ("Blinding Lights",        "Pop",      2019, "The Weeknd"),
        ("Bohemian Rhapsody",      "Rock",     1975, "Queen"),
        ("Starboy",                "R&B",      2016, "The Weeknd"),
        ("Shape of You",           "Pop",      2017, "Ed Sheeran"),
        ("Levitating",             "Pop",      2020, "Dua Lipa"),
        ("Smells Like Teen Spirit","Rock",     1991, "Nirvana"),
        ("Hotel California",       "Rock",     1977, "Eagles"),
        ("Stairway to Heaven",     "Rock",     1971, "Led Zeppelin"),
        ("Thriller",               "Pop",      1982, "Michael Jackson"),
        ("Billie Jean",            "Pop",      1982, "Michael Jackson"),
        ("Rolling in the Deep",    "Soul",     2010, "Adele"),
        ("Someone Like You",       "Soul",     2011, "Adele"),
        ("Stay With Me",           "Soul",     2014, "Sam Smith"),
        ("Thinking Out Loud",      "Pop",      2014, "Ed Sheeran"),
        ("Perfect",                "Pop",      2017, "Ed Sheeran"),
        ("Uptown Funk",            "Pop",      2014, "Bruno Mars"),
        ("24K Magic",              "R&B",      2016, "Bruno Mars"),
        ("Happier",                "Pop",      2018, "Marshmello"),
        ("Rockstar",               "Hip-Hop",  2017, "Post Malone"),
        ("Sunflower",              "Hip-Hop",  2018, "Post Malone"),
        ("God's Plan",             "Hip-Hop",  2018, "Drake"),
        ("One Dance",              "Hip-Hop",  2016, "Drake"),
        ("HUMBLE",                 "Hip-Hop",  2017, "Kendrick Lamar"),
        ("DNA",                    "Hip-Hop",  2017, "Kendrick Lamar"),
        ("Old Town Road",          "Country",  2019, "Lil Nas X"),
        ("Bad Guy",                "Pop",      2019, "Billie Eilish"),
        ("Happier Than Ever",      "Pop",      2021, "Billie Eilish"),
        ("Watermelon Sugar",       "Pop",      2019, "Harry Styles"),
        ("As It Was",              "Pop",      2022, "Harry Styles"),
        ("Anti-Hero",              "Pop",      2022, "Taylor Swift"),
        ("Shake It Off",           "Pop",      2014, "Taylor Swift"),
        ("Love Story",             "Country",  2008, "Taylor Swift"),
        ("Circles",                "Pop",      2019, "Post Malone"),
        ("Peaches",                "R&B",      2021, "Justin Bieber"),
        ("Stay",                   "Pop",      2021, "Justin Bieber"),
        ("Save Your Tears",        "Pop",      2020, "The Weeknd"),
        ("Heat Waves",             "Indie",    2020, "Glass Animals"),
        ("Drivers License",        "Pop",      2021, "Olivia Rodrigo"),
        ("good 4 u",               "Pop",      2021, "Olivia Rodrigo"),
        ("Industry Baby",          "Hip-Hop",  2021, "Lil Nas X"),
        ("Montero",                "Pop",      2021, "Lil Nas X"),
        ("Easy On Me",             "Soul",     2021, "Adele"),
        ("About Damn Time",        "Pop",      2022, "Lizzo"),
        ("Running Up That Hill",   "Rock",     1985, "Kate Bush"),
        ("Rich Flex",              "Hip-Hop",  2022, "Drake"),
        ("Flowers",                "Pop",      2023, "Miley Cyrus"),
        ("Cruel Summer",           "Pop",      2019, "Taylor Swift"),
        ("Escapism",               "R&B",      2022, "Raye"),
        ("Creepin",                "R&B",      2023, "The Weeknd"),
        ("Ella Baila Sola",        "Latin",    2023, "Eslabon Armado"),
    ]
    song_ids = [safe_add_media(t, "song", g, y, c) for t, g, y, c in songs_data]

    # ──────────────────────────────────────────────
    # Reviews — each user reviews 10 random media
    # ──────────────────────────────────────────────
    print("\n✍️  Adding reviews...")

    import random
    all_media_ids = movie_ids + show_ids + song_ids
    comments = [
        "Absolutely loved it!",
        "A masterpiece in every way.",
        "Highly recommended!",
        "Could have been better.",
        "One of my all time favorites.",
        "Surprisingly good!",
        "Decent but not great.",
        "Blew my mind completely.",
        "Would watch/listen again.",
        "Overrated in my opinion.",
        "Hidden gem — everyone should try it.",
        "Not my cup of tea.",
        "Incredible experience overall.",
        "Left me speechless.",
        "Pretty average honestly.",
    ]

    for user_id in user_ids:
        # pick 10 unique media for each user
        chosen = random.sample([m for m in all_media_ids if m is not None], 10)
        for media_id in chosen:
            rating  = round(random.uniform(5.0, 10.0), 1)
            comment = random.choice(comments)
            safe_add_review(user_id, media_id, rating, comment)

    # ──────────────────────────────────────────────
    # Favorites — each user favorites 5 random media
    # ──────────────────────────────────────────────
    print("\n❤️  Adding favorites...")
    for user_id in user_ids:
        chosen = random.sample([m for m in all_media_ids if m is not None], 5)
        for media_id in chosen:
            safe_add_favorite(user_id, media_id)

    print("\n✅ Seeding complete!")
    print("\n📊 Summary:")
    print(f"   👤 Users     : {len(user_ids)}")
    print(f"   🎬 Movies    : {len(movie_ids)}")
    print(f"   📺 Web Shows : {len(show_ids)}")
    print(f"   🎵 Songs     : {len(song_ids)}")
    print(f"   ✍️  Reviews   : {len(user_ids) * 10} (10 per user)")
    print(f"   ❤️  Favorites : {len(user_ids) * 5} (5 per user)")


if __name__ == "__main__":
    seed()