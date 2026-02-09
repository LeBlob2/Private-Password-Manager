import sqlite3
import os
from pathlib import Path

#Finds the Documents directory and puts it in there
path = os.path.abspath(os.path.dirname(__file__))
database = os.path.join(path, "Passwords.db")

#for debugging delete after build
print("Documents directory is:", path)
if not os.path.exists(path):
    os.makedirs(path)


with sqlite3.connect('Passwords.db') as connection: #This stores it in the python directory for now but should be in Documents in later versions

      cursor = connection.cursor()
      cursor.execute("DROP TABLE IF EXISTS Passwords")
      create_table_query = """
      CREATE TABLE Passwords (
      id INTEGER PRIMARY KEY, 
      username TEXT NOT NULL,
      email TEXT,
      password TEXT,
      phone INTEGER,
      extra TEXT,
      extranum INTEGER
      );
      """
      cursor.execute(create_table_query)
      connection.commit()
      print("Database and Table made") #For debug only use a message window for the real thing