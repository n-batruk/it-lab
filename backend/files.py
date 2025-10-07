import os
import shutil
from werkzeug.utils import secure_filename
from backend.database import add_file, get_user_files, get_file_by_id, delete_file, update_file_modified

STORAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'storage')
ALLOWED_EXTENSIONS = {'.c', '.jpg', '.jpeg'}  # Варіант 7

def init_storage():
    """Створити папку для файлів"""
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)
        print(f"✅ Створено папку storage: {STORAGE_PATH}")

def get_user_storage_path(user_id):
    """Отримати шлях до папки користувача"""
    user_path = os.path.join(STORAGE_PATH, f'user_{user_id}')
    if not os.path.exists(user_path):
        os.makedirs(user_path)
    return user_path

def is_allowed_file(filename):
    """Перевірити чи дозволене розширення файлу"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def save_uploaded_file(file, user_id, username):
    """Зберегти завантажений файл"""
    if not file:
        return None, "Файл не надано"
    
    filename = secure_filename(file.filename)
    
    if not filename:
        return None, "Невірне ім'я файлу"
    
    # Отримати розширення
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Шлях збереження
    user_storage = get_user_storage_path(user_id)
    filepath = os.path.join(user_storage, filename)
    
    # Якщо файл існує, додати номер
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{base_name}_{counter}{ext}"
        filepath = os.path.join(user_storage, filename)
        counter += 1
    
    # Зберегти файл
    try:
        file.save(filepath)
        file_size = os.path.getsize(filepath)
    except Exception as e:
        return None, f"Помилка збереження файлу: {str(e)}"
    
    # Додати до бази
    file_id = add_file(
        user_id=user_id,
        filename=filename,
        filepath=filepath,
        file_extension=file_extension,
        uploaded_by=username,
        file_size=file_size
    )
    
    return file_id, "Файл успішно завантажено"

def get_files_list(user_id, sort_by='created_at', sort_order='desc', file_filter='all'):
    """Отримати список файлів з фільтрацією та сортуванням"""
    # Якщо фільтр не 'all', перевіряємо чи він валідний
    if file_filter != 'all' and not file_filter.startswith('.'):
        file_filter = f'.{file_filter}'
    
    files = get_user_files(user_id, sort_by, sort_order, file_filter if file_filter != 'all' else None)
    
    # Форматування дат
    for file in files:
        if file['created_at']:
            file['created_at'] = file['created_at']
        if file['modified_at']:
            file['modified_at'] = file['modified_at']
    
    return files

def get_file_content(file_id, user_id):
    """Отримати вміст файлу для перегляду"""
    file = get_file_by_id(file_id)
    
    if not file or file['user_id'] != user_id:
        return None, None, "Файл не знайдено"
    
    filepath = file['filepath']
    
    if not os.path.exists(filepath):
        return None, None, "Файл не існує на диску"
    
    file_extension = file['file_extension']
    
    # Для .c файлів - читаємо як текст
    if file_extension == '.c':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return 'text', content, None
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
                return 'text', content, None
            except Exception as e:
                return None, None, f"Помилка читання файлу: {str(e)}"
    
    # Для .jpg файлів - повертаємо шлях
    elif file_extension in ['.jpg', '.jpeg']:
        return 'image', filepath, None
    
    return None, None, "Непідтримуваний тип файлу для перегляду"

def download_file(file_id, user_id):
    """Отримати шлях до файлу для завантаження"""
    file = get_file_by_id(file_id)
    
    if not file or file['user_id'] != user_id:
        return None, "Файл не знайдено"
    
    filepath = file['filepath']
    
    if not os.path.exists(filepath):
        return None, "Файл не існує на диску"
    
    return filepath, None

def remove_file(file_id, user_id):
    """Видалити файл"""
    file = get_file_by_id(file_id)
    
    if not file or file['user_id'] != user_id:
        return False, "Файл не знайдено"
    
    # Видалити з диску
    try:
        if os.path.exists(file['filepath']):
            os.remove(file['filepath'])
    except Exception as e:
        return False, f"Помилка видалення файлу: {str(e)}"
    
    # Видалити з бази
    deleted = delete_file(file_id, user_id)
    
    if deleted:
        return True, "Файл успішно видалено"
    else:
        return False, "Помилка видалення з бази даних"

# Ініціалізація при імпорті
init_storage()