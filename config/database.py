"""
config/database.py
MongoDB connection and collection management
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys


# ─── MongoDB Configuration ────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "MovieManagementSystem"


class Database:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """Establish MongoDB connection."""
        try:
            cls._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            cls._client.admin.command("ping")
            cls._db = cls._client[DATABASE_NAME]
            print(f"[✓] Connected to MongoDB: {DATABASE_NAME}")
            cls._ensure_indexes()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[✗] MongoDB connection failed: {e}")
            return False

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def _ensure_indexes(cls):
        """Create indexes for performance."""
        try:
            cls._db.users.create_index("username", unique=True)
            cls._db.users.create_index("email", unique=True)
            cls._db.movies.create_index("title")
            cls._db.reviews.create_index([("movie_id", 1), ("user_id", 1)])
            cls._db.favorites.create_index([("user_id", 1), ("movie_id", 1)])
        except Exception as e:
            print(f"Index creation warning: {e}")

    # ─── Collection Accessors ─────────────────────────────────────────────────
    @classmethod
    def users(cls):
        return cls.get_db().users

    @classmethod
    def movies(cls):
        return cls.get_db().movies

    @classmethod
    def genres(cls):
        return cls.get_db().genres

    @classmethod
    def reviews(cls):
        return cls.get_db().reviews

    @classmethod
    def favorites(cls):
        return cls.get_db().favorites

    @classmethod
    def reports(cls):
        return cls.get_db().reports

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            print("[✓] MongoDB connection closed.")
