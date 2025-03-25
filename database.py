import sqlite3
from datetime import datetime

DB_PATH = 'signals.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            strategy_name TEXT,
            signal INTEGER,
            result INTEGER,
            position_size REAL,
            entry_price REAL,
            leverage INTEGER,
            timestamp TEXT,
            user_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_signal(symbol, strategy_name, signal, result, position_size, entry_price, leverage, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO signals (symbol, strategy_name, signal, result, position_size, entry_price, leverage, timestamp, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (symbol, strategy_name, signal, result, position_size, entry_price, leverage, datetime.utcnow().isoformat(), user_id))
    conn.commit()
    conn.close()

def get_all_signals(strategy=None, symbol=None, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM signals WHERE 1=1"
    params = []
    if strategy:
        query += " AND strategy_name=?"
        params.append(strategy)
    if symbol:
        query += " AND symbol=?"
        params.append(symbol)
    if user_id:
        query += " AND user_id=?"
        params.append(user_id)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(["id", "symbol", "strategy_name", "signal", "result", "position_size", "entry_price", "leverage", "timestamp", "user_id"], row)) for row in rows]
