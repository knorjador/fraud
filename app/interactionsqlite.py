import sqlite3

con = sqlite3.connect("app.db")
cur = con.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

print(tables)  # Affiche la liste des tables existantes dans la base de données
