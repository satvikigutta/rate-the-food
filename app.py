import secrets
import sqlite3
import os

from flask import Flask, render_template_string
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["DATABASE_PATH"] = os.environ.get("DATABASE_PATH", "food.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


def init_db():
    connection = sqlite3.connect(app.config["DATABASE_PATH"])
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, place_id)
            );
            """
        )

        with connection:
            connection.execute("BEGIN IMMEDIATE")
            place_count = connection.execute(
                "SELECT COUNT(*) FROM places"
            ).fetchone()[0]
            if place_count == 0:
                usernames = [
                    "campus_taster",
                    "lunch_loop",
                    "snack_scout",
                    "coffee_breaker",
                    "weekend_bites",
                ]
                connection.executemany(
                    "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
                    [
                        (username, generate_password_hash(secrets.token_urlsafe(32)))
                        for username in usernames
                    ],
                )

                places = [
                    (
                        "The Campus Kettle",
                        "Cafe",
                        "West of the main quad",
                        "A small fictional cafe for coffee, toast, and quick breakfasts.",
                    ),
                    (
                        "Juniper Noodle House",
                        "Noodles",
                        "North of campus",
                        "A fictional counter serving noodle bowls with a few rotating broths.",
                    ),
                    (
                        "Coyote Corner Kitchen",
                        "American",
                        "Near the campus entrance",
                        "A fictional casual spot for sandwiches, salads, and loaded fries.",
                    ),
                    (
                        "Saffron & Lime",
                        "Mediterranean",
                        "A short walk east of campus",
                        "A fictional takeout kitchen with wraps, rice plates, and bright sauces.",
                    ),
                    (
                        "Little Orchard Bento",
                        "Japanese",
                        "South of campus",
                        "A fictional lunch counter with bento boxes and seasonal sides.",
                    ),
                    (
                        "Redwood Slice Co.",
                        "Pizza",
                        "A few blocks from campus",
                        "A fictional neighborhood pizza shop with slices and simple salads.",
                    ),
                    (
                        "Mango Moon Juice Bar",
                        "Juice and smoothies",
                        "Near the campus library",
                        "A fictional juice bar blending fruit smoothies and acai bowls.",
                    ),
                    (
                        "Tortilla Trail",
                        "Mexican",
                        "Northwest of campus",
                        "A fictional taqueria with burritos, tacos, and a salsa bar.",
                    ),
                    (
                        "Golden Wok Express",
                        "Chinese",
                        "Along the nearby shopping street",
                        "A fictional quick-service kitchen for stir-fries and rice plates.",
                    ),
                    (
                        "Poppyseed Bakehouse",
                        "Bakery",
                        "Southwest of campus",
                        "A fictional bakery with pastries, cookies, and sandwiches at lunch.",
                    ),
                ]
                connection.executemany(
                    """
                    INSERT INTO places (name, category, location, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    places,
                )

                user_ids = dict(
                    connection.execute("SELECT username, id FROM users").fetchall()
                )
                place_ids = dict(
                    connection.execute("SELECT name, id FROM places").fetchall()
                )
                reviews = [
                    ("campus_taster", "The Campus Kettle", 5, "Quick service and a very good cappuccino."),
                    ("campus_taster", "Juniper Noodle House", 4, "Comforting broth; I would ask for extra greens."),
                    ("campus_taster", "Coyote Corner Kitchen", 3, "A dependable sandwich when I am short on time."),
                    ("campus_taster", "Saffron & Lime", 5, "Fresh flavors and a generous rice plate."),
                    ("campus_taster", "Little Orchard Bento", 4, "Balanced bento and nicely seasoned vegetables."),
                    ("campus_taster", "Redwood Slice Co.", 2, "The crust was fine, but my slice was lukewarm."),
                    ("lunch_loop", "Juniper Noodle House", 5, "The spicy noodles had a great kick."),
                    ("lunch_loop", "Coyote Corner Kitchen", 4, "Good portions and an easy place for lunch."),
                    ("lunch_loop", "Saffron & Lime", 4, "Loved the lemony sauce; a little busy at noon."),
                    ("lunch_loop", "Little Orchard Bento", 3, "Tasty, though I wanted a bit more rice."),
                    ("lunch_loop", "Redwood Slice Co.", 5, "Crisp edges and a nicely balanced tomato sauce."),
                    ("lunch_loop", "Mango Moon Juice Bar", 4, "Refreshing smoothie with no overpowering sweetness."),
                    ("snack_scout", "Coyote Corner Kitchen", 2, "Friendly staff, but the fries were too salty."),
                    ("snack_scout", "Saffron & Lime", 5, "The chickpea wrap was bright and filling."),
                    ("snack_scout", "Little Orchard Bento", 4, "A neat, satisfying lunch with crisp pickles."),
                    ("snack_scout", "Redwood Slice Co.", 4, "Nice chewy crust and a generous topping."),
                    ("snack_scout", "Mango Moon Juice Bar", 5, "The mango bowl made a great afternoon snack."),
                    ("snack_scout", "Tortilla Trail", 3, "Solid tacos; the salsa bar is the best part."),
                    ("coffee_breaker", "Saffron & Lime", 3, "Good ingredients, though the wrap needed more sauce."),
                    ("coffee_breaker", "Little Orchard Bento", 5, "Fresh, quick, and easy to customize."),
                    ("coffee_breaker", "Redwood Slice Co.", 3, "A decent slice, especially for a quick stop."),
                    ("coffee_breaker", "Mango Moon Juice Bar", 4, "Smooth texture and a useful range of add-ins."),
                    ("coffee_breaker", "Tortilla Trail", 5, "Great roasted salsa and a filling burrito."),
                    ("coffee_breaker", "Golden Wok Express", 2, "The vegetables were a little softer than I like."),
                    ("weekend_bites", "Little Orchard Bento", 2, "Convenient, but the rice was dry on my visit."),
                    ("weekend_bites", "Redwood Slice Co.", 4, "A generous slice and friendly counter service."),
                    ("weekend_bites", "Mango Moon Juice Bar", 3, "Pleasant drink, though the size felt small."),
                    ("weekend_bites", "Tortilla Trail", 4, "Tasty tacos with a good choice of salsas."),
                    ("weekend_bites", "Golden Wok Express", 5, "The garlic noodles were flavorful and fast."),
                    ("weekend_bites", "Poppyseed Bakehouse", 4, "Excellent pastry and a cozy place to take a break."),
                ]
                connection.executemany(
                    """
                    INSERT INTO reviews (user_id, place_id, rating, text)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        (user_ids[username], place_ids[place_name], rating, text)
                        for username, place_name, rating, text in reviews
                    ],
                )
    finally:
        connection.close()


@app.get("/")
def home():
    return render_template_string(
        '{% extends "base.html" %}'
        '{% block content %}'
        '<h1>Rate the Food</h1>'
        '<p>Discover and rate places to eat near Santa Clara University.</p>'
        '{% endblock %}'
    )


init_db()


if __name__ == "__main__":
    app.run(debug=True)