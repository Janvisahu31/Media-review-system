import redis
import json

# ──────────────────────────────────────────────
# Connection
# ──────────────────────────────────────────────

try:
    client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2
    )
    client.ping()
    REDIS_AVAILABLE = True
    print("✅ Redis connected successfully")
except Exception:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available — running without cache")


# ──────────────────────────────────────────────
# TTL Constants (how long cache lives)
# ──────────────────────────────────────────────

TTL_TOP_RATED = 300   # 5 minutes
TTL_SEARCH    = 120   # 2 minutes
TTL_REVIEWS   = 60    # 1 minute
TTL_RECOMMENDATIONS = 180   # 3 minutes

# ──────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────

def get_cache(key: str):
    """Get a value from Redis cache."""
    if not REDIS_AVAILABLE:
        return None
    try:
        value = client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def set_cache(key: str, value, ttl: int):
    """Store a value in Redis cache with expiry time."""
    if not REDIS_AVAILABLE:
        return
    try:
        client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass


def delete_cache(key: str):
    """Delete a specific cache key."""
    if not REDIS_AVAILABLE:
        return
    try:
        client.delete(key)
    except Exception:
        pass


def flush_all_cache():
    """Clear entire cache — useful after bulk operations."""
    if not REDIS_AVAILABLE:
        return
    try:
        client.flushdb()
        print("🗑️  Cache cleared.")
    except Exception:
        pass


def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    if not REDIS_AVAILABLE:
        return False
    try:
        return client.exists(key) > 0
    except Exception:
        return False