import os

from flask import Flask, render_template_string

app = Flask(__name__)
app.config["DATABASE_PATH"] = os.environ.get("DATABASE_PATH", "food.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


@app.get("/")
def home():
    return render_template_string(
        '{% extends "base.html" %}'
        '{% block content %}'
        '<h1>Rate the Food</h1>'
        '<p>Discover and rate places to eat near Santa Clara University.</p>'
        '{% endblock %}'
    )


if __name__ == "__main__":
    app.run(debug=True)