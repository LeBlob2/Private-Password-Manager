import sqlite3

# This file is for opening and writing to an exsiting database

with sqlite3.connect('Passwords.db') as connection:
    cursor = connection.cursor()