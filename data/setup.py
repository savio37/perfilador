import sqlite3

con = sqlite3.connect("data/database.db")
cur = con.cursor()

with open("data/schema.sql") as sql_file:
    script = sql_file.read()
    
cur.executescript(script)

cur.execute("INSERT INTO identidades (nome, idade, pronomes, profissao) VALUES ('Geralt', 98, 'ele/dele', 'Bruxo')")
cur.execute("INSERT INTO identidades (nome, idade, pronomes, profissao) VALUES ('Yennefer', 94, 'ela/dela', 'Feiticeira')")

con.commit()
con.close()