import bcrypt
import secrets
from datetime import datetime, timedelta
from backend.database import create_user, get_user_by_username

# Простий in-memory storage для токенів (для production використовуйте Redis)
active_tokens = {}

def hash_password(password):
    """Хешувати пароль"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Перевірити пароль"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token():
    """Згенерувати токен сесії"""
    return secrets.token_urlsafe(32)

def register_user(username, password):
    """Реєстрація нового користувача"""
    # Валідація
    if not username or len(username) < 3:
        return None, "Ім'я користувача має бути мінімум 3 символи"
    
    if not password or len(password) < 6:
        return None, "Пароль має бути мінімум 6 символів"
    
    # Хешування паролю
    password_hash = hash_password(password)
    
    # Створення користувача
    user_id = create_user(username, password_hash)
    
    if user_id is None:
        return None, "Користувач з таким іменем вже існує"
    
    return user_id, "Реєстрація успішна"

def login_user(username, password):
    """Авторизація користувача"""
    user = get_user_by_username(username)
    
    if not user:
        return None, None, "Невірне ім'я користувача або пароль"
    
    if not verify_password(password, user['password_hash']):
        return None, None, "Невірне ім'я користувача або пароль"
    
    # Генерація токену
    token = generate_token()
    active_tokens[token] = {
        'user_id': user['id'],
        'username': user['username'],
        'created_at': datetime.now()
    }
    
    return user['id'], token, "Авторизація успішна"

def verify_token(token):
    """Перевірити токен"""
    if not token or token not in active_tokens:
        return None
    
    token_data = active_tokens[token]
    
    # Перевірка терміну дії (24 години)
    if datetime.now() - token_data['created_at'] > timedelta(hours=24):
        del active_tokens[token]
        return None
    
    return token_data

def logout_user(token):
    """Вийти з системи"""
    if token in active_tokens:
        del active_tokens[token]
        return True
    return False

def get_user_from_token(token):
    """Отримати дані користувача з токену"""
    token_data = verify_token(token)
    if token_data:
        return token_data['user_id'], token_data['username']
    return None, None