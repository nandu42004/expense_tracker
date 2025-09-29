-- schema.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  amount NUMERIC NOT NULL,    -- use NUMERIC/DECIMAL semantics (stored as text/number in SQLite)
  date TEXT NOT NULL,         -- store as 'YYYY-MM-DD'
  note TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- sample data for quick testing
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');

INSERT INTO categories (name) VALUES ('Groceries');
INSERT INTO categories (name) VALUES ('Utilities');
INSERT INTO categories (name) VALUES ('Entertainment');

INSERT INTO expenses (user_id, category_id, amount, date, note) VALUES (1, 1, '450.75', '2025-09-05', 'Weekly groceries');
INSERT INTO expenses (user_id, category_id, amount, date, note) VALUES (1, 2, '120.50', '2025-09-10', 'Electric bill');
INSERT INTO expenses (user_id, category_id, amount, date, note) VALUES (2, 3, '35.00', '2025-08-15', 'Movie ticket');
