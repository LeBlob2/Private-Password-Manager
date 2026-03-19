import os
import hashlib
import random
import string
import sqlcipher3

# base directory for all databases
db_path = os.path.expanduser("~/Documents/Passwords")

if not os.path.exists(db_path):
    os.makedirs(db_path)


def list_databases() -> list[str]:
    """Return all .db filenames (without extension) found in db_path."""
    return [
        f[:-3] for f in os.listdir(db_path)
        if f.endswith(".db") and os.path.exists(os.path.join(db_path, f + ".salt"))
    ]


def resolve_db_path(db_name: str) -> str:
    """Convert a database name to its full path."""
    return os.path.join(db_path, db_name + ".db")


# this converts the password to a hash because of course we need to do that
def derive_key(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 256000)
    return key.hex()


# salt for the hash and as the name says there
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


def get_connection(db_password: str, db_path: str):
    if not os.path.exists(db_path):
        return create_encrypted_database(db_path, db_password)
    else:
        return open_encrypted_database(db_path, db_password)


def generate_password(length: int = 16) -> str:
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


def delete_password_by_id(conn, entry_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (entry_id,))
    conn.commit()
    if cursor.rowcount == 0:
        return False

    # makes sure ID is always ordered 1,2,3 after deletion
    cursor.execute("SELECT id FROM users ORDER BY id")
    rows = cursor.fetchall()
    for new_id, (old_id,) in enumerate(rows, start=1):
        if new_id != old_id:
            cursor.execute("UPDATE users SET id = ? WHERE id = ?", (new_id, old_id))

    # reset the counter to 1 after deletion
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


def change_master_password(db_path: str, current_password: str, new_password: str) -> None:
    """
    Re-encrypts the database with a new master password.
    Generates a fresh salt, derives a new key, and uses SQLCipher's
    PRAGMA rekey to reencrypt in place, then overwrites the salt file.
    Raises ValueError if the current password is wrong.
    """
    conn = open_encrypted_database(db_path, current_password)

    new_salt = os.urandom(32)
    new_key = derive_key(new_password, new_salt)

    cursor = conn.cursor()
    cursor.execute(f"PRAGMA rekey = \"x'{new_key}'\";")
    conn.commit()
    conn.close()

    salt_path = db_path + '.salt'
    with open(salt_path, 'wb') as f:
        f.write(new_salt)
