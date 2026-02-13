import sqlite3

# This file is for opening and writing to an exsiting database

path = os.path.expanduser("~/Documents/Passwords")
database = os.path.join(path, "Passwords.db")

with sqlite3.connect(database) as connection:
    cursor = connection.cursor()