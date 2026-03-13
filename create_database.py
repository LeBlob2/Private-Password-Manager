import sqlite3
import sqlcipher3
import os
import hashlib
from pathlib import Path

# Path setup
path = os.path.expanduser("~/Documents/Passwords")
db_path = os.path.join(path, "test.db")

print("Documents directory is:", path)

if not os.path.exists(path):
    os.makedirs(path)

def derive_key(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=600000,
        dklen=32
    )
    return key.hex()

def create_encrypted_database(db_path: str, password: str, table_name: str = "Passwords"):
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

if __name__ == "__main__":
    password = input("Enter database password: ")

    if not os.path.exists(db_path):
        print("Creating new encrypted database...")
        conn = create_encrypted_database(db_path, password)
    else:
        print("Opening existing encrypted database...")
        conn = open_encrypted_database(db_path, password)

    print("Database ready!")
    conn.close()