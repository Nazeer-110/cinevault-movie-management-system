"""
seed_data.py
Populate MongoDB with sample data for testing.
Run once: python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
import datetime
from config.database import Database

Database.connect()

# ── Clear existing ──────────────────────────────────────────────────────────────
for col in [Database.users(), Database.movies(), Database.genres(),
            Database.reviews(), Database.favorites()]:
    col.delete_many({})

print("Seeding genres…")
genres = [
    {"name": "Action",     "description": "High-energy action films"},
    {"name": "Drama",      "description": "Emotional and character-driven stories"},
    {"name": "Comedy",     "description": "Lighthearted and humorous films"},
    {"name": "Sci-Fi",     "description": "Science fiction and futuristic themes"},
    {"name": "Horror",     "description": "Scary and suspenseful films"},
    {"name": "Romance",    "description": "Love stories and relationships"},
    {"name": "Thriller",   "description": "Suspenseful and gripping narratives"},
    {"name": "Animation",  "description": "Animated feature films"},
]
Database.genres().insert_many(genres)

print("Seeding users…")
def make_pw(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt())

users = [
    {"name": "Admin User",    "username": "admin",  "email": "admin@cinevault.com",
     "password": make_pw("admin123"),  "role": "admin", "status": "active"},
    {"name": "Alice Johnson",  "username": "alice",  "email": "alice@example.com",
     "password": make_pw("alice123"),  "role": "user",  "status": "active"},
    {"name": "Bob Smith",      "username": "bob",    "email": "bob@example.com",
     "password": make_pw("bob123"),    "role": "user",  "status": "active"},
    {"name": "Carol White",    "username": "carol",  "email": "carol@example.com",
     "password": make_pw("carol123"),  "role": "user",  "status": "blocked"},
]
result  = Database.users().insert_many(users)
user_ids = result.inserted_ids

print("Seeding movies…")
movies = [
    {"title": "Inception",     "genre": "Sci-Fi",   "director": "Christopher Nolan",
     "year": 2010, "duration": 148, "language": "English", "rating": 8.8,
     "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task.",
     "poster": "", "trailer": "https://www.youtube.com/watch?v=YoHD9XEInc0"},
    {"title": "The Dark Knight","genre": "Action",   "director": "Christopher Nolan",
     "year": 2008, "duration": 152, "language": "English", "rating": 9.0,
     "description": "Batman raises the stakes in his war on crime against the Joker.",
     "poster": "", "trailer": ""},
    {"title": "Parasite",      "genre": "Thriller",  "director": "Bong Joon-ho",
     "year": 2019, "duration": 132, "language": "Korean",  "rating": 8.5,
     "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between two families.",
     "poster": "", "trailer": ""},
    {"title": "Interstellar",  "genre": "Sci-Fi",   "director": "Christopher Nolan",
     "year": 2014, "duration": 169, "language": "English", "rating": 8.6,
     "description": "A team of explorers travel through a wormhole in space to ensure humanity's survival.",
     "poster": "", "trailer": ""},
    {"title": "Forrest Gump",  "genre": "Drama",    "director": "Robert Zemeckis",
     "year": 1994, "duration": 142, "language": "English", "rating": 8.8,
     "description": "The presidencies of Kennedy and Johnson through the eyes of an Alabama man with a low IQ.",
     "poster": "", "trailer": ""},
    {"title": "The Grand Budapest Hotel", "genre": "Comedy", "director": "Wes Anderson",
     "year": 2014, "duration": 99, "language": "English", "rating": 8.1,
     "description": "Adventures of a legendary hotel concierge and his trusty lobby boy.",
     "poster": "", "trailer": ""},
    {"title": "Get Out",       "genre": "Horror",   "director": "Jordan Peele",
     "year": 2017, "duration": 104, "language": "English", "rating": 7.7,
     "description": "A Black man uncovers a disturbing secret when he visits his white girlfriend's family.",
     "poster": "", "trailer": ""},
    {"title": "Spider-Man: Into the Spider-Verse", "genre": "Animation",
     "director": "Bob Persichetti", "year": 2018, "duration": 117, "language": "English",
     "rating": 8.4, "description": "Miles Morales becomes the Spider-Man of his universe.",
     "poster": "", "trailer": ""},
]
m_result = Database.movies().insert_many(movies)
movie_ids = m_result.inserted_ids

print("Seeding reviews…")
reviews = [
    {"movie_id": movie_ids[0], "user_id": user_ids[1], "rating": 5,
     "review": "Mind-bending masterpiece! The concept of shared dreaming is executed brilliantly.",
     "date": datetime.datetime(2024, 1, 15).isoformat()},
    {"movie_id": movie_ids[0], "user_id": user_ids[2], "rating": 4,
     "review": "Visually stunning with a complex but rewarding narrative.",
     "date": datetime.datetime(2024, 2, 10).isoformat()},
    {"movie_id": movie_ids[1], "user_id": user_ids[1], "rating": 5,
     "review": "Best superhero film ever made. Ledger's Joker is iconic.",
     "date": datetime.datetime(2024, 3, 5).isoformat()},
    {"movie_id": movie_ids[4], "user_id": user_ids[2], "rating": 5,
     "review": "A timeless classic that moves you to tears every time.",
     "date": datetime.datetime(2024, 4, 20).isoformat()},
]
Database.reviews().insert_many(reviews)

print("Seeding favorites…")
Database.favorites().insert_many([
    {"user_id": user_ids[1], "movie_id": movie_ids[0]},
    {"user_id": user_ids[1], "movie_id": movie_ids[1]},
    {"user_id": user_ids[2], "movie_id": movie_ids[3]},
])

print("\n✓ Seed data inserted successfully!")
print("\nTest credentials:")
print("  Admin  – username: admin   password: admin123")
print("  User 1 – username: alice   password: alice123")
print("  User 2 – username: bob     password: bob123")
