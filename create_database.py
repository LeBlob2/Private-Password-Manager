import sqlite3
import os
import hashlib
from pathlib import Path

#Finds the Documents and Passwords directory. Uncomment for later releases
path = os.path.expanduser("~/Documents/Passwords")
db_path = os.path.join(path, "test.db")

#for debugging delete after build
print("Documents directory is:", path)

#makes sure we don't make the same folder again
if not os.path.exists(path):
    os.makedirs(path)

def derive_key(password: str, salt: bytes) -> str:
    """
    Derive a database encryption key from a user password.
    Uses PBKDF2 with SHA-256 and 600,000 iterations.
    """
    # Use PBKDF2 to derive a key from the password
    # 600,000 iterations is the OWASP recommendation for 2024
    password = input()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=600000,
        dklen=32  # 256 bits
    )
    # Return as hex string for SQLCipher
    return key.hex()

def create_encrypted_database(db_path: str, password: str):
    """Create a new encrypted database with a derived key."""
    # Generate a random salt and store it alongside the database
    salt = os.urandom(32)
    salt_path = db_path + '.salt'

    with open(salt_path, 'wb') as f:
        f.write(salt)

    # Derive the encryption key
    key = derive_key(password, salt)

    # Create the encrypted database
    conn = sqlcipher3.connect(db_path)
    cursor = conn.cursor()

    # Set the derived key
    cursor.execute(f"PRAGMA key = \"x'{key}'\"")

    # Configure cipher settings
    cursor.execute("PRAGMA cipher_page_size = 4096")
    cursor.execute("PRAGMA kdf_iter = 256000")

    return conn

def open_encrypted_database(db_path: str, password: str):
    """Open an existing encrypted database."""
    # Read the stored salt
    salt_path = db_path + '.salt'
    with open(salt_path, 'rb') as f:
        salt = f.read()

    # Derive the key using the same parameters
    key = derive_key(password, salt)

    conn = sqlcipher3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key = \"x'{key}'\"")

    # Verify the key is correct
    try:
        cursor.execute("SELECT count(*) FROM sqlite_master")
        return conn
    except sqlcipher3.DatabaseError:
        conn.close()
        raise ValueError("Invalid password")