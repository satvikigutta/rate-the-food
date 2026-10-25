import os
import secrets
import sqlite3
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DATABASE_PATH"] = os.environ.get("DATABASE_PATH", "food.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
MAX_REVIEW_LENGTH = 1000


def get_db_connection():
    connection = sqlite3.connect(app.config["DATABASE_PATH"])
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


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
    connection = get_db_connection()
    try:
        places = connection.execute(
            """
            SELECT p.id, p.name, p.category, p.location,
                   ROUND(AVG(r.rating), 1) AS average_rating,
                   COUNT(r.id) AS review_count
            FROM places AS p
            LEFT JOIN reviews AS r ON r.place_id = p.id
            GROUP BY p.id
            ORDER BY CASE WHEN COUNT(r.id) = 0 THEN 1 ELSE 0 END,
                     AVG(r.rating) DESC,
                     p.name COLLATE NOCASE
            """
        ).fetchall()
    finally:
        connection.close()
    return render_template("home.html", places=places)


@app.get("/place/<int:place_id>")
def place_detail(place_id):
    return render_place_page(place_id)


def render_place_page(place_id, form_rating=None, form_text=None):
    connection = get_db_connection()
    try:
        place = connection.execute(
            """
            SELECT p.id, p.name, p.category, p.location, p.description,
                   ROUND(AVG(r.rating), 1) AS average_rating,
                   COUNT(r.id) AS review_count
            FROM places AS p
            LEFT JOIN reviews AS r ON r.place_id = p.id
            WHERE p.id = ?
            GROUP BY p.id
            """,
            (place_id,),
        ).fetchone()
        if place is None:
            abort(404)

        reviews = connection.execute(
            """
            SELECT r.rating, r.text,
                   strftime('%Y-%m-%d', r.created_at) AS review_date,
                   u.username
            FROM reviews AS r
            JOIN users AS u ON u.id = r.user_id
            WHERE r.place_id = ?
            ORDER BY r.created_at DESC, r.id DESC
            """,
            (place_id,),
        ).fetchall()
        rating_rows = connection.execute(
            """
            SELECT rating, COUNT(*) AS count
            FROM reviews
            WHERE place_id = ?
            GROUP BY rating
            """,
            (place_id,),
        ).fetchall()
        rating_counts = [0, 0, 0, 0, 0]
        for rating_row in rating_rows:
            rating_counts[rating_row["rating"] - 1] = rating_row["count"]
        user_review = None
        if session.get("user_id") is not None:
            user_review = connection.execute(
                """
                SELECT rating, text FROM reviews
                WHERE user_id = ? AND place_id = ?
                """,
                (session["user_id"], place_id),
            ).fetchone()
    finally:
        connection.close()

    if form_rating is None:
        form_rating = str(user_review["rating"]) if user_review else ""
    if form_text is None:
        form_text = user_review["text"] if user_review else ""
    return render_template(
        "place.html",
        place=place,
        reviews=reviews,
        rating_counts=rating_counts,
        user_review=user_review,
        form_rating=form_rating,
        form_text=form_text,
        max_review_length=MAX_REVIEW_LENGTH,
    )


@app.post("/place/<int:place_id>/review")
@login_required
def submit_review(place_id):
    rating_value = request.form.get("rating", "")
    review_text = request.form.get("text", "")
    cleaned_text = review_text.strip()

    try:
        rating = int(rating_value)
    except ValueError:
        rating = 0

    if rating < 1 or rating > 5:
        flash("Choose a rating from 1 to 5.", "error")
        return render_place_page(place_id, rating_value, review_text)
    if not cleaned_text:
        flash("Review text cannot be empty.", "error")
        return render_place_page(place_id, rating_value, review_text)
    if len(review_text) > MAX_REVIEW_LENGTH:
        flash(
            f"Review text must be {MAX_REVIEW_LENGTH} characters or fewer.", "error"
        )
        return render_place_page(place_id, rating_value, review_text)

    connection = get_db_connection()
    try:
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            existing_review = connection.execute(
                "SELECT id FROM reviews WHERE user_id = ? AND place_id = ?",
                (session["user_id"], place_id),
            ).fetchone()
            if existing_review:
                connection.execute(
                    """
                    UPDATE reviews
                    SET rating = ?, text = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (rating, cleaned_text, existing_review["id"], session["user_id"]),
                )
                message = "Your review has been updated."
            else:
                connection.execute(
                    """
                    INSERT INTO reviews (user_id, place_id, rating, text)
                    VALUES (?, ?, ?, ?)
                    """,
                    (session["user_id"], place_id, rating, cleaned_text),
                )
                message = "Your review has been submitted."
    except sqlite3.IntegrityError:
        abort(404)
    finally:
        connection.close()

    flash(message, "success")
    return redirect(url_for("place_detail", place_id=place_id, _anchor="reviews"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Enter both a username and password.", "error")
            return render_template("register.html", username=username)

        connection = get_db_connection()
        try:
            with connection:
                connection.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
        except sqlite3.IntegrityError:
            flash("That username is already taken. Choose another one.", "error")
            return render_template("register.html", username=username)
        finally:
            connection.close()

        user = get_db_connection()
        try:
            account = user.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
        finally:
            user.close()
        session.clear()
        session["user_id"] = account["id"]
        session["username"] = username
        flash("Your account has been created.", "success")
        return redirect(url_for("home"))

    return render_template("register.html", username="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Enter both your username and password.", "error")
            return render_template("login.html", username=username)

        connection = get_db_connection()
        try:
            account = connection.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        finally:
            connection.close()

        if account is None or not check_password_hash(
            account["password_hash"], password
        ):
            flash("Invalid username or password.", "error")
            return render_template("login.html", username=username)

        session.clear()
        session["user_id"] = account["id"]
        session["username"] = account["username"]
        flash("You are now logged in.", "success")
        return redirect(url_for("home"))

    return render_template("login.html", username="")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)