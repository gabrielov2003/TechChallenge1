import sqlite3
import pandas as pd
import os

DB_PATH = 'instance/database.db'


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
        CREATE TABLE IF NOT EXISTS Clinete (
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
        
        CREATE TABLE IF NOT EXISTS Ordem_Servico (
            id_os INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_veiculo INTEGER NOT NULL,
            status TEXT DEFAULT 'Recebida',
            FOREIGN KEY(id_cliente) REFERENCES Clinete(id_cliente),
            FOREIGN KEY(id_veiculo) REFERENCES Veiculo(id_veiculo)
        );
        ''')
        conn.commit()
        conn.close()
        print("Banco de dados e tabelas (Clinete, Veiculo, Servicos, Pecar) inicializados.")

    @staticmethod
    def execute_query(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def fetch_pandas(query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn, params=params)