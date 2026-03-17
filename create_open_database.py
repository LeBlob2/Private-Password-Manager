import os
import hashlib
import random
import string
import sqlcipher3

#This is for the path to the document folder not sure if this works on windows
path = os.path.expanduser("~/Documents/Passwords")
db_path = os.path.join(path, "test.db")

print("Documents directory is:", path)

if not os.path.exists(path):
    os.makedirs(path)

#this converts the password to a hash because of course we need to do that
def derive_key(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 256000)
    return key.hex()

#salt for the hash and as the name says there
def create_encrypted_database(db_path: str, password: str, table_name: str = "users"):
    salt = os.urandom(32)
    salt_path = db_path + '.salt'
    with open(salt_path, 'wb') as f:
        f.write(salt)

    key = derive_key(password, salt)
    conn = sqlcipher3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA key = \"x'{key}'\";")
    cursor.execute("PRAGMA cipher_page_size = 4096;")
    cursor.execute("PRAGMA kdf_iter = 256000;")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return conn

#the function names are there you can read what they do
def open_encrypted_database(db_path: str, password: str):
    salt_path = db_path + '.salt'
    with open(salt_path, 'rb') as f:
        salt = f.read()

    key = derive_key(password, salt)
    conn = sqlcipher3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA key = \"x'{key}'\";")
    cursor.execute("PRAGMA cipher_page_size = 4096;")
    cursor.execute("PRAGMA kdf_iter = 256000;")

    try:
        cursor.execute("SELECT count(*) FROM sqlite_master;")
        return conn
    except sqlcipher3.DatabaseError:
        conn.close()
        raise ValueError("That is not your password dumbass.")

#checks if database already exists or not should have custom text for this but i cant be bothered
def get_connection(db_password: str, db_path: str = db_path):
    if not os.path.exists(db_path):
        return create_encrypted_database(db_path, db_password)
    else:
        return open_encrypted_database(db_path, db_password)

#change the int value for longer password, since most websites go to 32 max you can set it to that but 16 is the default
def generate_password(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(random.choice(chars) for _ in range(length))


def save_password(conn, website: str, username: str, email: str, password: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (website, username, email, password) VALUES (?, ?, ?, ?)",
        (website, username, email, password)
    )
    conn.commit()


def fetch_all_passwords(conn) -> list[tuple]:
    cursor = conn.cursor()
    cursor.execute("SELECT id, website, username, email, password, created_at FROM users")
    return cursor.fetchall()


def delete_entry(conn, entry_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (entry_id,))
    conn.commit()
    if cursor.rowcount == 0:
        return False

    #sets the id to be in order after an entry is deleted very cheap hack i know
    cursor.execute("SELECT id FROM users ORDER BY id")
    rows = cursor.fetchall()
    for new_id, (old_id,) in enumerate(rows, start=1):
        if new_id != old_id:
            cursor.execute("UPDATE users SET id = ? WHERE id = ?", (new_id, old_id))

    #sets the id back to one after deletion and increments by current entries already in it
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
    cursor.execute("SELECT MAX(id) FROM users")
    max_id = cursor.fetchone()[0] or 0
    if max_id > 0:
        cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('users', ?)", (max_id,))

    conn.commit()
    return True


def update_password(conn, email: str, new_password: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password, email)
    )
    conn.commit()
