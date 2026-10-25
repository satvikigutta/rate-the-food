# Rate the Food

A Flask app for discovering and reviewing places to eat on and around Santa Clara University.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. Set `DATABASE_PATH` to choose a SQLite database file and `SECRET_KEY` to configure Flask's secret key.