# Rate the Food

A Flask app for discovering and reviewing places to eat on and around Santa Clara University.

The SQLite tables are created automatically at startup. An empty database is populated with fictional sample places, users, and reviews.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. To run with the production WSGI server locally:

```sh
gunicorn -b 127.0.0.1:8000 app:app
```

Set `DATABASE_PATH` to choose a SQLite database file and `SECRET_KEY` to configure Flask's secret key. The parent directory for the database is created automatically. Use a strong `SECRET_KEY` outside local development.

## Deploy to Cloud Run

With the Google Cloud CLI installed, authenticated, and configured for your project, deploy from this directory:

```sh
gcloud run deploy --source .
```

Cloud Run uses the `Procfile` to start Gunicorn. The container's local filesystem is temporary and is not shared between instances, so its SQLite database is suitable for a demo but not durable production storage.