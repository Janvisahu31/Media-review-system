
> A CLI-based platform to review movies, web shows, and songs — built with Python, SQLite, Redis, Multithreading, and Design Patterns.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![Redis](https://img.shields.io/badge/Redis-Cache-red?style=flat-square&logo=redis)
![Tests](https://img.shields.io/badge/Tests-76%20Passing-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technologies](#-technologies)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Setup & Installation](#-setup--installation)
- [CLI Commands](#-cli-commands)
- [Architecture & Design Patterns](#-architecture--design-patterns)
- [Multi-User Sessions](#-multi-user-sessions)
- [Redis Caching](#-redis-caching)
- [Multithreading](#-multithreading)
- [Git Workflow](#-git-workflow)
- [Running Tests](#-running-tests)
- [Known Limitations](#-known-limitations)

---

## 🌟 Overview

The **Media Review System** is a fully featured command-line application that allows users to review, rate, and discover movies, web shows, and songs. It demonstrates a production-grade architecture using:

- **SQLAlchemy ORM** for database interaction
- **Redis** for caching frequently accessed data
- **Multithreading** for concurrent bulk review submissions
- **Factory Pattern** for structured media type creation
- **Observer Pattern** for real-time review notifications
- **bcrypt** for secure password hashing
- **Per-terminal session management** for simultaneous multi-user support

---

## ✅ Features

| Feature | Description |
|---|---|
| 👤 User Management | Register, login, logout, change password |
| 🎬 Media Storage | Add and manage Movies, Web Shows, Songs |
| ✍️ Reviews & Ratings | Submit reviews with ratings (1.0–10.0) |
| 📂 Bulk Reviews | Submit multiple reviews from a CSV file concurrently |
| 🔍 Search | Search media by title with Redis-cached results |
| ⭐ Top Rated | Leaderboard of highest rated media |
| 💡 Recommendations | Personalized suggestions based on your taste |
| 🔔 Notifications | Get notified of new reviews on favorited media |
| 🔐 Authentication | bcrypt hashing + per-terminal sessions |
| ⚡ Performance | Redis caching + multithreading metrics |

---

## 🛠️ Technologies

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core development |
| SQLAlchemy | 2.0.36 | ORM for database interaction |
| SQLite | Built-in | Relational data storage |
| Redis | 5.2.1 | Caching top-rated and search results |
| bcrypt | 4.2.1 | Password hashing and verification |
| pytest | 9.0.2 | Unit testing framework |
| pytest-cov | 6.0.0 | Test coverage reporting |
| Docker | Latest | Running Redis container |

---

## 📁 Project Structure

```

media_review_system/
│
├── media_review.py          # CLI entry point — all commands live here
├── seed_data.py             # Idempotent seeder — 50 users, movies, shows, songs
├── reviews.csv              # Sample bulk review file
├── start.sh                 # Git Bash terminal session setup
├── start.ps1                # PowerShell terminal session setup
├── requirements.txt         # Python dependencies
│
├── database/
│   ├── db.py                # SQLite engine, SessionLocal, init_db()
│   └── models.py            # ORM models: User, Media, Review, Favorite
│
├── services/
│   ├── user_service.py      # add_user, get_user_by_id, get_by_email
│   ├── media_service.py     # add_media, search_by_title, get_all, get_by_id
│   └── review_service.py    # submit_review, bulk_submit, top_rated, recommend
│
├── patterns/
│   ├── factory.py           # MediaFactory → Movie / WebShow / Song
│   └── observer.py          # ReviewSubject + UserObserver + notifications
│
├── cache/
│   └── redis_client.py      # get_cache, set_cache, delete_cache, TTL constants
│
├── utils/
│   └── auth.py              # hash_password, login, logout, login_required decorator
│
└── tests/
    ├── conftest.py           # Shared fixtures: test_user, test_media, test_review
    ├── test_auth.py          # 21 tests — hashing, register, login, sessions
    ├── test_user.py          # 8 tests  — CRUD, password hashing
    ├── test_media.py         # 12 tests — add, search, factory validation
    ├── test_review.py        # 13 tests — submit, ratings, top-rated, recommend
    ├── test_factory.py       # 14 tests — all types, invalid, get_details, to_db_model
    └── test_observer.py      # 9 tests  — favorites, notify, subject

```

### What Each File Does

| File | Responsibility | Talks To |
|---|---|---|
| `media_review.py` | Parses CLI flags, routes to handlers | All services |
| `database/db.py` | Creates SQLite engine and session factory | models.py |
| `database/models.py` | Defines User, Media, Review, Favorite tables | db.py |
| `services/user_service.py` | User CRUD with password hashing | models, auth |
| `services/media_service.py` | Media operations + Redis search cache | models, factory, cache |
| `services/review_service.py` | Reviews, bulk submit, recommendations | models, cache, observer |
| `patterns/factory.py` | Validates and creates typed media objects | media_service |
| `patterns/observer.py` | Favorites management and notifications | review_service |
| `cache/redis_client.py` | Redis read/write with TTL and fallback | review_service, media_service |
| `utils/auth.py` | bcrypt hashing, per-terminal sessions | user_service |

---

## 🗄️ Database Schema

### Tables

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  users   │──────<│ reviews  │>──────│  media   │
│----------│       │----------│       │----------│
│ id       │       │ id       │       │ id       │
│ name     │       │ user_id  │       │ title    │
│ email    │       │ media_id │       │media_type│
│ password │       │ rating   │       │ genre    │
│created_at│       │ comment  │       │release_yr│
└──────────┘       │created_at│       │ creator  │
     │             └──────────┘       │created_at│
     │                                └──────────┘
     │             ┌──────────┐            │
     └────────────<│favorites │>───────────┘
                   │----------│
                   │ id       │
                   │ user_id  │
                   │ media_id │
                   └──────────┘
```

### Column Details

**users**
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(150) | UNIQUE, NOT NULL |
| password | VARCHAR(255) | NOT NULL (bcrypt hashed) |
| created_at | DATETIME | DEFAULT now() |

**media**
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| title | VARCHAR(200) | NOT NULL |
| media_type | ENUM | movie \| web_show \| song |
| genre | VARCHAR(100) | — |
| release_year | INTEGER | — |
| creator | VARCHAR(150) | Director / Artist |
| created_at | DATETIME | DEFAULT now() |

**reviews**
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| user_id | INTEGER | FK → users.id |
| media_id | INTEGER | FK → media.id |
| rating | FLOAT | NOT NULL, 1.0–10.0 |
| comment | TEXT | — |
| created_at | DATETIME | DEFAULT now() |

**favorites**
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| user_id | INTEGER | FK → users.id |
| media_id | INTEGER | FK → media.id |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Docker or Rancher Desktop
- Git

### Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd media_review_system
```

### Step 2 — Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows PowerShell
venv\Scripts\activate

# Git Bash / Mac / Linux
source venv/Scripts/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Start Redis

```bash
# Pull and run Redis container
docker run -d --name redis-server -p 6379:6379 redis

# Verify it is running
docker exec -it redis-server redis-cli ping
# Expected: PONG
```

### Step 5 — Initialize and Seed Database

```bash
# Initialize tables
python media_review.py --list

# Seed with 50 users, movies, shows, songs
python seed_data.py
```

### Step 6 — Set Terminal Identity (Required for Multi-User)

```powershell
# PowerShell — run once per terminal window
$env:MEDIA_TERMINAL_ID = $PID

# Git Bash — run once per terminal window
export MEDIA_TERMINAL_ID=$$

# Or use the helper scripts
.\start.ps1      # PowerShell
source start.sh  # Git Bash
```

---

## 🖥️ CLI Commands

### Public Commands (No Login Required)

```bash
# List all media
python media_review.py --list

# Search media by title (partial match)
python media_review.py --search "Inception"

# Get top 5 rated media
python media_review.py --top-rated
```

### Authentication Commands

```bash
# Register a new account
python media_review.py --register <name> <email> <password>

Ex - python media_review.py --register "Alice" alice@example.com pass123

# Login
python media_review.py --login <email> <password>

Ex - python media_review.py --login alice@example.com pass123

# Check who is logged in
python media_review.py --whoami

# Change password
python media_review.py --change-password oldpass newpass

# Logout
python media_review.py --logout
```

### Protected Commands (Login Required)

```bash
# Submit a single review
python media_review.py --review <media_id> <rating> <comment>
python media_review.py --review 1 9.0 "One of the best films ever!"

# Bulk submit from CSV file
python media_review.py --bulk-review reviews.csv

# Get personalized recommendations
python media_review.py --recommend

# Add media to favorites
python media_review.py --favorite <media_id>

# Check new reviews on your favorited media
python media_review.py --notification
```

### All Commands Reference

| Command | Parameters | Login Required | Description |
|---|---|---|---|
| `--list` | None | ❌ | List all media |
| `--search` | TITLE | ❌ | Search by title |
| `--top-rated` | None | ❌ | Top 5 rated media |
| `--register` | NAME EMAIL PASSWORD | ❌ | Create account |
| `--login` | EMAIL PASSWORD | ❌ | Login |
| `--logout` | None | ✅ | Logout |
| `--whoami` | None | ❌ | Show current user |
| `--change-password` | OLD NEW | ✅ | Change password |
| `--review` | MEDIA_ID RATING COMMENT | ✅ | Submit review |
| `--bulk-review` | FILE_PATH | ✅ | Bulk CSV submit |
| `--recommend` | None | ✅ | Recommendations |
| `--favorite` | MEDIA_ID | ✅ | Add to favorites |
| `--notification` | None | ✅ | Check notifications |

### Bulk Review CSV Format

```csv
media_id,rating,comment
1,8.5,Great movie loved it
2,9.0,Absolutely brilliant
3,7.5,Good but could be better
```

---

## 🏗️ Architecture & Design Patterns

### Application Layers

```
CLI Layer         media_review.py
    ↓             argparse reads flags → routes to handlers
Service Layer     user_service / media_service / review_service
    ↓             business logic, validation, error handling
Pattern Layer     factory.py / observer.py
    ↓             Factory creates objects, Observer sends notifications
Cache Layer       redis_client.py
    ↓             check Redis before DB, invalidate on write
Database Layer    db.py / models.py
                  SQLAlchemy ORM → SQLite
```

### Factory Pattern

Creates the correct media object based on type — validated and structured.

```python
# Without Factory — error prone
Media(title="Inception", media_type="movie", ...)

# With Factory — validated and structured
MediaFactory.create("movie", "Inception", "Sci-Fi", 2010, "Nolan")
# → Movie object with get_details() and to_db_model()
```

Adding a new media type requires only:
1. Create a new class inheriting `BaseMedia`
2. Add one line to `MediaFactory._creators` dict

### Observer Pattern

Users subscribe to media via `--favorite`. When `--notification` is called, only reviews posted **after the user's last login** are shown.

```
User favorites media  →  Favorite record in DB
      ↓
--notification called
      ↓
Find all favorites for logged-in user
      ↓
Find reviews AFTER last_seen timestamp
      ↓
ReviewSubject.notify_all() → prints new reviews
      ↓
update_last_seen() → next call shows only newer ones
```
# 🏗️ Architecture — Deep Dive

## Application Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI LAYER                                │
│                     media_review.py                             │
│                                                                 │
│  argparse reads flags → validates input → routes to handlers    │
│                                                                 │
│  Functions:  main(), build_parser(), handle_*()                 │
│  Concept:    Command routing, argument parsing, decorator-based │
│              auth guard (login_required)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│          user_service / media_service / review_service          │
│                                                                 │
│  What we are trying to do:                                      │
│  Keep the CLI thin. All business logic lives here.              │
│  CLI never touches the database directly.                       │
│                                                                 │
│  user_service.py                                                │
│  ├── add_user(name, email, password)                            │
│  │       → hashes password via auth.hash_password()             │
│  │       → checks duplicate email                               │
│  │       → saves User ORM object to DB                          │
│  ├── get_user_by_id(user_id)                                    │
│  ├── get_user_by_email(email)                                   │
│  └── get_all_users()                                            │
│                                                                 │
│  media_service.py                                               │
│  ├── add_media(title, type, genre, year, creator)               │
│  │       → calls MediaFactory.create() for validation           │
│  │       → checks duplicate                                     │
│  │       → calls to_db_model() → saves to DB                    │
│  ├── get_all_media()      → formatted table output              │
│  ├── search_by_title(title)  → checks Redis → then DB           │
│  └── get_media_by_id(media_id)                                  │
│                                                                 │
│  review_service.py                                              │
│  ├── submit_review(user_id, media_id, rating, comment)          │
│  │       → validates rating (1.0–10.0)                          │
│  │       → checks user + media exist                            │
│  │       → checks no duplicate review                           │
│  │       → saves Review → invalidates Redis cache               │
│  ├── submit_review_thread(...)   → thread-safe version          │
│  ├── bulk_submit_reviews(file, user_id)                         │
│  │       → reads CSV → spawns N threads → joins all             │
│  │       → measures + prints performance metrics                │
│  ├── get_top_rated(limit)   → checks Redis → then DB            │
│  ├── get_recommendations(user_id)                               │
│  │       → finds genres user rated >= 7.0                       │
│  │       → excludes already reviewed media                      │
│  │       → returns unreviewed media in liked genres             │
│  └── get_reviews_by_media(media_id)                             │
│                                                                 │
│  Concept: Separation of Concerns — each service owns one        │
│  domain. Session management pattern — open → use → close.       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PATTERN LAYER                              │
│                 factory.py / observer.py                        │
│                                                                 │
│──── FACTORY PATTERN (factory.py) ───────────────────────────────│
│                                                                 │
│  What we are trying to do:                                      │
│  Different media types (movie/song/show) need different         │
│  display formats and validation. Instead of if/else chains,     │
│  a factory decides which class to create.                       │
│                                                                 │
│  Classes:                                                       │
│  ├── BaseMedia          → abstract parent, defines interface    │
│  │   ├── get_details()  → raises NotImplementedError            │
│  │   └── to_db_model()  → raises NotImplementedError            │
│  ├── Movie(BaseMedia)   → media_type = MOVIE                    │
│  │   ├── get_details()  → shows "Director:" label               │
│  │   └── to_db_model()  → returns Media ORM object              │
│  ├── WebShow(BaseMedia) → media_type = WEB_SHOW                 │
│  │   ├── get_details()  → shows "Creator:" label                │
│  │   └── to_db_model()  → returns Media ORM object              │
│  ├── Song(BaseMedia)    → media_type = SONG                     │
│  │   ├── get_details()  → shows "Artist:" label                 │
│  │   └── to_db_model()  → returns Media ORM object              │
│  └── MediaFactory                                               │
│      ├── _creators = {"movie": Movie, "web_show": ..., ...}     │
│      ├── create(type, ...)  → dict lookup → returns object      │
│      └── supported_types() → returns valid type list            │
│                                                                 │
│  Concept: Factory Pattern — centralises object creation.        │
│  Open/Closed Principle — add new types without changing         │
│  existing code. Just add a class + one line in _creators.       │
│                                                                 │
│  ── OBSERVER PATTERN (observer.py) ─────────────────────────── │
│                                                                 │
│  What we are trying to do:                                      │
│  When a new review is posted, notify users who care about       │
│  that media — without the review system knowing about users.    │
│                                                                 │
│  Classes:                                                       │
│  ├── Observer (interface)                                       │
│  │   └── notify(media_title, reviewer, rating, comment)         │
│  ├── UserObserver(Observer)                                     │
│  │   └── notify() → prints formatted notification to terminal   │
│  ├── ReviewSubject                                              │
│  │   ├── attach(observer)   → adds to _observers list           │
│  │   ├── detach(observer)   → removes from list                 │
│  │   └── notify_all(...)    → loops and calls each observer     │
│  └── Helper functions:                                          │
│      ├── add_favorite(user_id, media_id)                        │
│      │       → checks duplicate → saves Favorite to DB          │
│      └── get_notifications(user_id, last_seen)                  │
│              → finds user's favorites                           │
│              → finds reviews AFTER last_seen timestamp          │
│              → builds ReviewSubject + attaches UserObserver     │
│              → calls notify_all()                               │
│              → calls update_last_seen() so they don't repeat    │
│                                                                 │
│  Concept: Observer Pattern — decouples event producer           │
│  (new review) from event consumers (subscribed users).          │
│  last_seen timestamp acts as a read-receipt.                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CACHE LAYER                               │
│                      redis_client.py                            │
│                                                                 │
│  What we are trying to do:                                      │
│  Avoid hitting the database for the same query repeatedly.      │
│  Store results in Redis memory with an expiry time (TTL).       │
│  On write operations, invalidate stale cache.                   │
│                                                                 │
│  Functions:                                                     │
│  ├── get_cache(key)          → returns parsed JSON or None      │
│  ├── set_cache(key, value, ttl) → stores JSON with expiry       │
│  ├── delete_cache(key)       → removes specific key             │
│  ├── flush_all_cache()       → clears entire Redis DB           │
│  └── cache_exists(key)       → checks if key present            │
│                                                                 │
│  TTL Constants:                                                 │
│  ├── TTL_TOP_RATED = 300s  (5 minutes)                          │
│  └── TTL_SEARCH    = 120s  (2 minutes)                          │
│                                                                 │
│  Cache Flow:                                                    │
│  read  → check Redis → hit? return it : query DB → store in     │
│          Redis → return result                                  │
│  write → save to DB → delete_cache("top_rated:5")               │
│                                                                 │
│  Concept: Cache-Aside Pattern. REDIS_AVAILABLE flag means       │
│  the app degrades gracefully if Redis is down — it just         │
│  skips caching and hits DB directly. No crash.                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                             │
│                    db.py / models.py                            │
│                                                                 │
│  What we are trying to do:                                      │
│  Define the database structure as Python classes (ORM) and      │
│  manage connections safely so sessions never leak.              │
│                                                                 │
│  db.py                                                          │
│  ├── engine = create_engine("sqlite:///media_review.db")        │
│  │       → single connection to SQLite file                     │
│  ├── SessionLocal = sessionmaker(bind=engine)                   │
│  │       → factory that creates DB sessions on demand           │
│  ├── Base = declarative_base()                                  │
│  │       → parent class all models inherit from                 │
│  ├── get_db()    → generator that yields + always closes        │
│  └── init_db()   → creates all tables if not exist              │
│                                                                 │
│  models.py                                                      │
│  ├── MediaType(Enum)  → MOVIE | WEB_SHOW | SONG                 │
│  ├── User(Base)                                                 │
│  │   └── relationships → reviews, favorites                     │
│  ├── Media(Base)                                                │
│  │   └── relationships → reviews, favorites                     │
│  ├── Review(Base)                                               │
│  │   └── relationships → user, media (FK both ways)             │
│  └── Favorite(Base)                                             │
│      └── relationships → user, media                            │
│                                                                 │
│  Concept: ORM (Object Relational Mapping) — interact with DB    │
│  using Python objects instead of raw SQL. Session pattern —     │
│  every function opens a session, uses try/except/finally to     │
│  guarantee the session closes even if an error occurs.          │
│                                                                 │
│  Session Pattern used everywhere:                               │
│  db = SessionLocal()                                            │
│  try:                                                           │
│      # do work                                                  │
│  except:                                                        │
│      db.rollback()                                              │
│  finally:                                                       │
│      db.close()   ← ALWAYS runs                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧵 Multithreading — How It Works

```
What we are trying to do:
Process many reviews at the same time instead of one by one.

bulk_submit_reviews(file_path, user_id)
    │
    ├── Read CSV → parse into list of dicts
    │
    ├── results = [None] * len(reviews)    ← pre-allocated result slots
    │
    ├── For each review:
    │       thread = Thread(target=submit_review_thread, args=(..., i))
    │       thread.start()    ← all threads running simultaneously
    │
    ├── For each thread:
    │       thread.join()     ← wait for ALL threads to finish
    │
    ├── with db_lock:         ← threading.Lock()
    │       db.add(review)    ← only ONE thread writes at a time
    │       db.commit()       ← prevents data corruption
    │
    └── Print results + time taken + avg per review

Key concepts:
  threading.Thread  → creates a concurrent unit of execution
  thread.start()    → begins running concurrently
  thread.join()     → blocks until that thread finishes
  threading.Lock()  → mutual exclusion — one thread at a time
  results[index]    → thread-safe via pre-allocated slots (no append)
```

---

## 🔐 Authentication — How It Works

```
What we are trying to do:
Secure user accounts with hashed passwords and
isolate each terminal's login state independently.

Registration:
  plain password
      │
      ▼
  bcrypt.gensalt()         ← random salt generated
      │
      ▼
  bcrypt.hashpw(password, salt)   ← one-way hash
      │
      ▼
  "$2b$12$eImiTXuWV..."   ← stored in DB (never plain text)

Login:
  user types password
      │
      ▼
  bcrypt.checkpw(plain, stored_hash)   ← verify without decrypting
      │
      ├── True  → write .session_<TERMINAL_ID>.json
      └── False → "Incorrect password"

Per-Terminal Sessions:
  $env:MEDIA_TERMINAL_ID = $PID    ← set once per terminal
      │
      ▼
  get_session_file()
      │
      ▼
  ".session_27216.json"    ← unique per terminal
      │
  Each command reads only its own session file
  Multiple users work simultaneously without interference

login_required decorator:
  @login_required
  def handle_review(args, user):
      ...
      │
      ▼
  Wraps any handler — checks session file exists
  If not logged in → prints error and returns early
  If logged in     → passes user data to handler function

Key concepts:
  bcrypt          → adaptive hashing — slow by design to resist brute force
  salt            → random value so same password = different hash each time
  decorator       → wraps functions to add behaviour without changing them
  env variable    → inherited by child processes — stable per terminal
```

---

## 🔄 Complete Request Flow — Example

**`python media_review.py --review 1 9.0 "Great film!"`**

```
1. media_review.py
   argparse reads: --review 1 9.0 "Great film!"
   args.review = ["1", "9.0", "Great film!"]

2. login_required decorator
   reads .session_27216.json
   user = {"user_id": 1, "name": "Alice", ...}
   passes user to handle_review()

3. handle_review(args, user)
   calls submit_review(user_id=1, media_id=1, rating=9.0, comment="Great film!")

4. review_service.submit_review()
   ├── validates rating: 1.0 <= 9.0 <= 10.0 ✅
   ├── db.query(User).filter(id=1).first()     → Alice found ✅
   ├── db.query(Media).filter(id=1).first()    → Inception found ✅
   ├── db.query(Review).filter(...).first()    → no duplicate ✅
   ├── Review(user_id=1, media_id=1, rating=9.0, ...) created
   ├── db.add() → db.commit() → saved to SQLite
   └── delete_cache("top_rated:5")             → Redis invalidated

5. Output:
   ✅ Review submitted for 'Inception' by Alice | Rating: 9.0/10
```
---

## 👥 Multi-User Sessions

Each terminal gets its own session file based on `MEDIA_TERMINAL_ID`:

```
Terminal 1 ($PID=27216) → .session_27216.json → Alice logged in
Terminal 2 ($PID=45891) → .session_45891.json → Bob logged in
```

Both users work simultaneously without interfering — similar to how Ubuntu handles multiple terminal tabs.

```bash
# Terminal 1
$env:MEDIA_TERMINAL_ID = $PID
python media_review.py --login alice@example.com pass123
python media_review.py --whoami   # → Alice

# Terminal 2 (simultaneously)
$env:MEDIA_TERMINAL_ID = $PID
python media_review.py --login bob@example.com pass456
python media_review.py --whoami   # → Bob

# Terminal 1 is unaffected
python media_review.py --whoami   # → still Alice
```

---

## ⚡ Redis Caching

| Command | Cache Key | TTL | Invalidated When |
|---|---|---|---|
| `--top-rated` | `top_rated:5` | 5 minutes | New review submitted |
| `--search TITLE` | `search:<title>` | 2 minutes | TTL expiry only |

```
First call  → DB query → store in Redis → return result
Second call → Redis hit → return instantly (no DB query)
New review  → delete top_rated cache → next call hits DB
```

---

## 🧵 Multithreading

Bulk reviews are submitted concurrently — one thread per review — with a `threading.Lock()` preventing simultaneous DB writes.

```bash
python media_review.py --bulk-review reviews.csv

# Output
📂 Found 5 reviews in 'reviews.csv'
🚀 Submitting concurrently using 5 threads...

✅ Row 1: Review submitted for 'Inception' | Rating: 8.5/10
✅ Row 2: Review submitted for 'Breaking Bad' | Rating: 9.0/10
✅ Row 3: Review submitted for 'Blinding Lights' | Rating: 7.5/10

────────────────────────────────────────
✅ Successful : 3
❌ Failed     : 0
📊 Total      : 3
⏱️  Time taken : 0.0842 seconds
⚡ Avg/review : 28.07 ms
────────────────────────────────────────
```

---

## 🌿 Git Workflow

### Branch History

```
main
 ├── feature/database-models
 ├── feature/user-service
 ├── feature/media-service
 ├── feature/review-service
 ├── feature/factory-pattern
 ├── feature/observer-pattern
 ├── feature/bulk-review-multithreading
 ├── feature/redis-caching
 ├── feature/authentication
 ├── feature/unit-tests
 └── feature/documentation
```

### Commit Convention

```
feature:     new feature
fix:      bug fix
chore:    config, deps, tooling
docs:     documentation
test:     adding/updating tests
refactor: code change, no feature or fix
```

**Examples:**
```bash
git commit -m "feat: add Redis caching for top-rated results"
git commit -m "fix: correct bcrypt hashing in add_user"
git commit -m "test: add 76 unit tests for all services"
```

---

## 🧪 Running Tests

```bash
# Run all 76 tests
pytest tests/ -v

# Run with coverage report
pytest --cov=services --cov=patterns --cov=utils --cov=database --cov-report=term-missing

# Run specific file
pytest tests/test_auth.py -v
```

### Test Summary

| File | Tests | Coverage |
|---|---|---|
| test_auth.py | 21 | hashing, register, login, sessions, change password |
| test_factory.py | 14 | all types, invalid type, get_details, to_db_model |
| test_media.py | 12 | add, duplicate, invalid type, search, get by id |
| test_review.py | 13 | submit, bounds, duplicate, top-rated, recommend |
| test_observer.py | 9 | favorites, notify, subject, notifications |
| test_user.py | 8 | add, duplicate email, password hashing, get by id |
| **Total** | **76** | **All services, patterns, and utilities** |

---

## ⚠️ Known Limitations

- `MEDIA_TERMINAL_ID` must be set manually per terminal on Windows
- Recommendations are genre-based only (not collaborative filtering)
- No pagination on `--list` with 150+ media items
- No media edit or delete commands

---

## 🔮 Future Improvements

- [ ] JWT token-based auth (like `kubectl` / `aws-cli`)
- [ ] Collaborative filtering recommendations
- [ ] Pagination for `--list`
- [ ] Media edit and delete commands
- [ ] REST API layer on top of the services
- [ ] Docker Compose for app + Redis together
- [ ] Export reviews to CSV or PDF

---

## 👤 Author

**Janvi Hariprasad Sahu**

---

