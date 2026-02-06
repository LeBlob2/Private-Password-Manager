import sqlite3
import os

#Finds the Documets directory and puts it in there
path = os.path.expanduser("~/Documents/Passwords")

#for debugging delete after build
print("Documents directory is:", path)
if not os.path.exists(path):
    os.makedirs(path)


with sqlite3.connect('Passwords.db') as connection: #This stores it in the python directory for now but should be in Documents in later versions

      cursor = connection.cursor()
      create_table_query = '''
      CREATE TABLE IF NOT EXIST Passwords (
      id INTEGER PRIMARY KEY AUTOINCREMENTAL, 
      username TEXT NOT NULL,
      email TEXT,
      password TEXT,
      phone INTEGER,
      extra TEXT,
      extranum INTEGER,
      );
      '''
      cursor.execute(create_table_query)
      connection.commit()
      print("Database and Table made") #For debug only use a message window for the real thing