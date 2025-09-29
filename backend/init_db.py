# init_db.py
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "db.sqlite"
SCHEMA = HERE / "schema.sql"

def init_db():
    if DB.exists():
        print("Database already exists:", DB)
        return
    with sqlite3.connect(DB) as conn, open(SCHEMA, "r", encoding="utf8") as f:
        sql = f.read()
        conn.executescript(sql)
    print("Initialized DB at", DB)

if __name__ == "__main__":
    init_db()
