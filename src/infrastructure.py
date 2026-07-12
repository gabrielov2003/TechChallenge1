import sqlite3
import pandas as pd
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.getenv('DATABASE_PATH', 'instance/database.db')


class Infrastructure:
    @staticmethod
    def get_connection():
        os.makedirs('instance', exist_ok=True)
        return sqlite3.connect(DB_PATH)

    @classmethod
    def init_db(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()

        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Cliente (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Veiculo (
            id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            marca TEXT,
            modelo TEXT,
            ano INTEGER
        );

        CREATE TABLE IF NOT EXISTS Peca (
            id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_unitario REAL NOT NULL,
            estoque INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Servico (
            id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Ordem_Servico (
            id_os INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_veiculo INTEGER NOT NULL,
            status TEXT DEFAULT 'Recebida',
            data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_fechamento DATETIME,
            FOREIGN KEY(id_cliente) REFERENCES Cliente(id_cliente),
            FOREIGN KEY(id_veiculo) REFERENCES Veiculo(id_veiculo)
        );

        CREATE TABLE IF NOT EXISTS Servicos_carro (
            id_os INTEGER,
            servico TEXT NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY(id_os) REFERENCES Ordem_Servico(id_os)
        );

        CREATE TABLE IF NOT EXISTS Pecas_carro (
            id_os INTEGER,
            peca TEXT NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY(id_os) REFERENCES Ordem_Servico(id_os)
        );

        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        );
        ''')

        for col in [
            "ALTER TABLE Ordem_Servico ADD COLUMN data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE Ordem_Servico ADD COLUMN data_fechamento DATETIME",
        ]:
            try:
                cursor.execute(col)
            except Exception:
                pass

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO Usuario (username, senha_hash) VALUES (?, ?)",
                ('admin', generate_password_hash('admin123'))
            )
            conn.commit()

        conn.close()
        print("Banco de dados inicializado.")

    @staticmethod
    def execute_query(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def execute_update(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def fetch_pandas(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn, params=params)

    @staticmethod
    def fetch_one(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None