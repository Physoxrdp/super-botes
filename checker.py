import requests
from datetime import datetime
from db import conn, cur

HEADERS = {"User-Agent": "Mozilla/5.0"}

def check_profile(username):
    r = requests.get(f"https://www.instagram.com/{username}/",
                     headers=HEADERS, timeout=10)
    if r.status_code == 200:
        return "VISIBLE"
    if r.status_code == 404:
        return "NOT_FOUND"
    return "TEMP"

def update_account(username):
    result = check_profile(username)
    cur.execute("SELECT last_status, confirm_count FROM accounts WHERE username=?", (username,))
    row = cur.fetchone()

    if not row:
        cur.execute("INSERT INTO accounts VALUES (?,?,?,?)",
                    (username, result, 1, datetime.utcnow()))
        conn.commit()
        return None

    last_status, count = row
    count = count + 1 if result == last_status else 1

    cur.execute("UPDATE accounts SET last_status=?, confirm_count=?, last_change=? WHERE username=?",
                (result, count, datetime.utcnow(), username))
    conn.commit()

    if count == 3:
        return result
    return None
