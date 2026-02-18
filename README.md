Project Structure 

media_review_system/
│
├── main.py                      # Entry point, CLI app init
├── .gitignore
├── requirements.txt
│
├── database/
│   ├── __init__.py
│   ├── db.py                    # Connection, engine, session setup
│   └── models.py                # All SQLAlchemy models here
│
├── services/
│   ├── __init__.py
│   ├── user_service.py          # User CRUD logic
│   ├── media_service.py         # Add/search media
│   └── review_service.py        # Submit/fetch reviews
│
├── patterns/
│   ├── __init__.py
│   ├── factory.py               # MediaFactory → Movie/Song/WebShow
│   └── observer.py              # ReviewSubject + UserObserver
│
├── cache/
│   ├── __init__.py
│   └── redis_client.py          # Cache get/set/invalidate helpers
│
├── utils/
│   ├── __init__.py
│   └── auth.py                  # Session/auth helpers (bonus)
│
└── tests/
    ├── __init__.py
    ├── test_user.py
    ├── test_media.py
    ├── test_review.py
    └── test_factory.py