import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
''')

cursor.execute("INSERT INTO usuarios (nome) VALUES ('João')")
cursor.execute("INSERT INTO usuarios (nome) VALUES ('Maria')")

conn.commit()
conn.close()

print("Banco criado com sucesso!")