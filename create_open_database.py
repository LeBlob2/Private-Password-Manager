import os
import hashlib
import random
import string
import sqlcipher3


DB_PATH = "secure.db"



def derive_key(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 256000)
    return key.hex()


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
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
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
        raise ValueError("Invalid password")


def get_connection(db_password: str, db_path: str = DB_PATH):
    if not os.path.exists(db_path):
        return create_encrypted_database(db_path, db_password)
    else:
        return open_encrypted_database(db_path, db_password)



def generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(random.choice(chars) for _ in range(length))


def save_password(conn, website: str, email: str, password: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (website, email, password)
    )
    conn.commit()


def fetch_all_passwords(conn) -> list[tuple]:
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password, created_at FROM users")
    return cursor.fetchall()


def delete_password(conn, email: str) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()


def update_password(conn, email: str, new_password: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password, email)
    )
    conn.commit()
