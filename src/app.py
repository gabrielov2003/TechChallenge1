from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "API rodando 🚀"

@app.route('/usuarios')
def listar_usuarios():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()

    return jsonify([dict(u) for u in usuarios])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)