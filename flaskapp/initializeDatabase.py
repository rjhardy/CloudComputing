import csv
import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS users""")
cur.execute("""CREATE TABLE users
            (username text, password text, firstname text, lastname text, email text)""")

with open('users.csv', 'r') as f:
    reader = csv.reader(f.readlines()[1:])  # exclude header line
    cur.executemany("""INSERT INTO users VALUES (?,?,?,?,?)""",
                    (row for row in reader))
conn.commit()
