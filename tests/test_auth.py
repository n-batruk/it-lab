import pytest
import sys
import os

# Додати шлях до backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.auth import hash_password, verify_password, register_user, login_user

def test_hash_password():
    """Тест 1: Хешування паролю"""
    password = "test123"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert len(hashed) > 0
    
    # Check that the hash is different from the original
    assert hashed != password
    
    # Check that two hashes of the same password are different (salt)
    hashed2 = hash_password(password)
    assert hashed != hashed2

def test_verify_password():
    """Тест 2: Перевірка паролю"""
    password = "mypassword123"
    hashed = hash_password(password)
    
    # Correct password
    assert verify_password(password, hashed) == True
    
    # Wrong password
    assert verify_password("wrongpassword", hashed) == False
    assert verify_password("", hashed) == False

def test_register_user():
    """Тест 3: Реєстрація користувача"""
    # Successful registration
    user_id, message = register_user("testuser123", "password123")
    assert user_id is not None
    assert "успішна" in message.lower()
    
    # Try to register the same user
    user_id2, message2 = register_user("testuser123", "password123")
    assert user_id2 is None
    assert "існує" in message2.lower()
    
    # Too short username
    user_id3, message3 = register_user("ab", "password123")
    assert user_id3 is None
    
    # Too short password
    user_id4, message4 = register_user("validuser", "12345")
    assert user_id4 is None

def test_login_user():
    """Тест 4: Авторизація користувача"""
    # Create test user
    username = "logintest"
    password = "testpass123"
    register_user(username, password)
    
    # Successful login
    user_id, token, message = login_user(username, password)
    assert user_id is not None
    assert token is not None
    assert len(token) > 0
    
    # Wrong password
    user_id2, token2, message2 = login_user(username, "wrongpass")
    assert user_id2 is None
    assert token2 is None
    
    # Unregistered user
    user_id3, token3, message3 = login_user("nonexistent", "pass")
    assert user_id3 is None
    assert token3 is None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])