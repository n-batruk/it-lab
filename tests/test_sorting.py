import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import init_db, create_user, add_file, get_connection
from backend.files import get_files_list
from backend.auth import hash_password

@pytest.fixture(scope='function')
def setup_test_sorting():
    import backend.database as db
    
    db.DB_PATH = 'test_sorting.db'
    init_db()
    
    user_id = create_user('sortuser', hash_password('password'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # File 1 - 3 days ago
    date1 = (datetime.now() - timedelta(days=3)).isoformat()
    cursor.execute('''
        INSERT INTO files (user_id, filename, filepath, file_extension, uploaded_by, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'old_file.txt', '/path/old.txt', '.txt', 'sortuser', 100, date1))
    
    # File 2 - 2 days ago
    date2 = (datetime.now() - timedelta(days=2)).isoformat()
    cursor.execute('''
        INSERT INTO files (user_id, filename, filepath, file_extension, uploaded_by, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'middle_file.c', '/path/middle.c', '.c', 'sortuser', 200, date2))
    
    # File 3 - 1 day ago
    date3 = (datetime.now() - timedelta(days=1)).isoformat()
    cursor.execute('''
        INSERT INTO files (user_id, filename, filepath, file_extension, uploaded_by, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'new_file.jpg', '/path/new.jpg', '.jpg', 'sortuser', 300, date3))
    
    conn.commit()
    conn.close()
    
    yield user_id
    
    if os.path.exists('test_sorting.db'):
        os.remove('test_sorting.db')

def test_sort_by_created_at_ascending(setup_test_sorting):
    user_id = setup_test_sorting
    
    files = get_files_list(user_id, sort_by='created_at', sort_order='asc')
    
    assert len(files) == 3
    
    assert files[0]['filename'] == 'old_file.txt'
    assert files[1]['filename'] == 'middle_file.c'
    assert files[2]['filename'] == 'new_file.jpg'
    
    date1 = datetime.fromisoformat(files[0]['created_at'])
    date2 = datetime.fromisoformat(files[1]['created_at'])
    date3 = datetime.fromisoformat(files[2]['created_at'])
    
    assert date1 < date2 < date3

def test_sort_by_created_at_descending(setup_test_sorting):
    user_id = setup_test_sorting
    
    files = get_files_list(user_id, sort_by='created_at', sort_order='desc')
    
    assert len(files) == 3
    
    assert files[0]['filename'] == 'new_file.jpg'
    assert files[1]['filename'] == 'middle_file.c'
    assert files[2]['filename'] == 'old_file.txt'
    
    date1 = datetime.fromisoformat(files[0]['created_at'])
    date2 = datetime.fromisoformat(files[1]['created_at'])
    date3 = datetime.fromisoformat(files[2]['created_at'])
    
    assert date1 > date2 > date3

def test_sort_with_filter(setup_test_sorting):
    user_id = setup_test_sorting
    
    files = get_files_list(user_id, sort_by='created_at', sort_order='desc', file_filter='.c')
    
    assert len(files) == 1
    assert files[0]['filename'] == 'middle_file.c'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])