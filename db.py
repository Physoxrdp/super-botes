import sqlite3
conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
  username TEXT PRIMARY KEY,
  last_status TEXT,
  confirm_count INTEGER,
  last_change TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS usernames (
  username TEXT PRIMARY KEY,
  status TEXT,
  confirm_count INTEGER,
  first_seen_available TEXT
)
""")
conn.commit()
