import sqlite3
import os

def new_database():
con = sqlite3.connect('PATH#/Passwords.db') #This stores it in the python directory for now but should allow for user to set the path
cur = con.cursor()
cur.execute("CREATE TABLE passwords(Username, Email, Password, Phone, Extra1, Extra2)") #We probably don't need so many fields but just in case we have them