import sqlite3
from datetime import datetime
import os

DB_PATH = 'database.db'

def init_db():
    """Ініціалізація бази даних"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблиця користувачів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця файлів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_extension TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by TEXT NOT NULL,
            edited_by TEXT,
            file_size INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База даних ініціалізована")

def get_connection():
    """Отримати з'єднання з БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Доступ до колонок по імені
    return conn

def create_user(username, password_hash):
    """Створити користувача"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Користувач вже існує

def get_user_by_username(username):
    """Отримати користувача по імені"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Отримати користувача по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def add_file(user_id, filename, filepath, file_extension, uploaded_by, file_size):
    """Додати файл до бази"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (user_id, filename, filepath, file_extension, uploaded_by, file_size)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, filename, filepath, file_extension, uploaded_by, file_size))
    conn.commit()
    file_id = cursor.lastrowid
    conn.close()
    return file_id

def get_user_files(user_id, sort_by='created_at', sort_order='desc', file_filter=None):
    """Отримати файли користувача з сортуванням та фільтрацією"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Базовий запит
    query = 'SELECT * FROM files WHERE user_id = ?'
    params = [user_id]
    
    # Фільтрація по розширенню
    if file_filter and file_filter != 'all':
        query += ' AND file_extension = ?'
        params.append(file_filter)
    
    # Сортування (варіант 1 - по даті створення)
    valid_columns = ['created_at', 'modified_at', 'filename', 'uploaded_by', 'edited_by']
    if sort_by in valid_columns:
        query += f' ORDER BY {sort_by}'
        if sort_order.lower() == 'asc':
            query += ' ASC'
        else:
            query += ' DESC'
    
    cursor.execute(query, params)
    files = cursor.fetchall()
    conn.close()
    
    return [dict(file) for file in files]

def get_file_by_id(file_id):
    """Отримати файл по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file = cursor.fetchone()
    conn.close()
    return dict(file) if file else None

def delete_file(file_id, user_id):
    """Видалити файл"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE id = ? AND user_id = ?', (file_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def update_file_modified(file_id, edited_by):
    """Оновити час модифікації файлу"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE files 
        SET modified_at = CURRENT_TIMESTAMP, edited_by = ?
        WHERE id = ?
    ''', (edited_by, file_id))
    conn.commit()
    conn.close()

# Ініціалізація при імпорті
if __name__ == '__main__':
    init_db()