import sqlite3
import os
from pathlib import Path

#Finds the Documents and Passwords directory. Uncomment for later releases
#path = os.path.expanduser("~/Documents/Passwords")
#database = os.path.join(path, "Passwords.db")

#for debugging delete after build
#print("Documents directory is:", path)

#makes sure we don't make the same folder again
#if not os.path.exists(path):
 #   os.makedirs(path)


with sqlite3.connect('Passwords.db') as connection: #This stores it in the python directory for now but should be in Documents/Passwords in the release version


      cursor = connection.cursor()
      cursor.execute("DROP TABLE IF EXISTS Passwords")
      create_table_query = """
      CREATE TABLE Passwords (
      PRAGMA key 'password'
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
      