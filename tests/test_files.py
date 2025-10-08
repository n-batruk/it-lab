import pytest
import sys
import os
import tempfile
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import init_db, create_user, add_file
from backend.files import save_uploaded_file, get_files_list, get_file_content, remove_file
from werkzeug.datastructures import FileStorage

@pytest.fixture(scope='function')
def setup_test_db():
    """Створити тестову базу даних та користувача"""
    import backend.database as db
    
    db.DB_PATH = 'test_database.db'
    init_db()
    
    from backend.auth import hash_password
    user_id = create_user('testuser', hash_password('password'))
    
    yield user_id
    
    if os.path.exists('test_database.db'):
        os.remove('test_database.db')

def test_save_uploaded_file(setup_test_db):
    """Тест 5: Збереження завантаженого файлу"""
    user_id = setup_test_db
    
    file_content = b"Test file content"
    file = FileStorage(
        stream=BytesIO(file_content),
        filename="test.txt",
        content_type="text/plain"
    )
    
    file_id, message = save_uploaded_file(file, user_id, 'testuser')
    
    assert file_id is not None
    assert "успішно" in message.lower()

def test_get_files_list(setup_test_db):
    """Тест 6: Отримання списку файлів"""
    user_id = setup_test_db
    
    add_file(user_id, 'file1.txt', '/path/file1.txt', '.txt', 'testuser', 100)
    add_file(user_id, 'file2.c', '/path/file2.c', '.c', 'testuser', 200)
    add_file(user_id, 'file3.jpg', '/path/file3.jpg', '.jpg', 'testuser', 300)
    
    files = get_files_list(user_id)
    assert len(files) == 3
    
    files_c = get_files_list(user_id, file_filter='.c')
    assert len(files_c) == 1
    assert files_c[0]['filename'] == 'file2.c'
    
    files_jpg = get_files_list(user_id, file_filter='.jpg')
    assert len(files_jpg) == 1
    assert files_jpg[0]['filename'] == 'file3.jpg'

def test_delete_file(setup_test_db):
    user_id = setup_test_db
    
    file_id = add_file(user_id, 'delete_test.txt', '/path/delete_test.txt', '.txt', 'testuser', 100)
    
    files_before = get_files_list(user_id)
    assert len(files_before) == 1
    
    success, message = remove_file(file_id, user_id)
    
    files_after = get_files_list(user_id)
    assert len(files_after) == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])