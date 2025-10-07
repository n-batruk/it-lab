from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from backend.database import init_db
from backend.auth import register_user, login_user, logout_user, verify_token, get_user_from_token
from backend.files import save_uploaded_file, get_files_list, get_file_content, download_file, remove_file
import os
import base64

app = Flask(__name__)
CORS(app)  # Дозволити CORS для десктоп-клієнта

# Ініціалізація бази даних
init_db()

# === АВТОРИЗАЦІЯ ===

@app.route('/api/register', methods=['POST'])
def api_register():
    """Реєстрація користувача"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_id, message = register_user(username, password)
    
    if user_id:
        return jsonify({'success': True, 'message': message, 'user_id': user_id}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    """Авторизація користувача"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_id, token, message = login_user(username, password)
    
    if token:
        return jsonify({
            'success': True,
            'message': message,
            'token': token,
            'user_id': user_id,
            'username': username
        }), 200
    else:
        return jsonify({'success': False, 'message': message}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Вихід з системи"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if logout_user(token):
        return jsonify({'success': True, 'message': 'Вихід успішний'}), 200
    else:
        return jsonify({'success': False, 'message': 'Токен не знайдено'}), 400

# === ФАЙЛИ ===

def require_auth(f):
    """Декоратор для перевірки авторизації"""
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        token_data = verify_token(token)
        
        if not token_data:
            return jsonify({'success': False, 'message': 'Не авторизовано'}), 401
        
        return f(token_data, *args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/files', methods=['GET'])
@require_auth
def api_get_files(token_data):
    """Отримати список файлів з фільтрацією та сортуванням"""
    user_id = token_data['user_id']
    
    # Параметри фільтрації та сортування (варіант 1)
    sort_by = request.args.get('sort_by', 'created_at')  # created_at для варіанту 1
    sort_order = request.args.get('sort_order', 'desc')  # desc або asc
    file_filter = request.args.get('filter', 'all')  # all, .c, .jpg
    
    files = get_files_list(user_id, sort_by, sort_order, file_filter)
    
    return jsonify({'success': True, 'files': files}), 200

@app.route('/api/upload', methods=['POST'])
@require_auth
def api_upload_file(token_data):
    """Завантажити файл"""
    user_id = token_data['user_id']
    username = token_data['username']
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не надано'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Файл не вибрано'}), 400
    
    file_id, message = save_uploaded_file(file, user_id, username)
    
    if file_id:
        return jsonify({'success': True, 'message': message, 'file_id': file_id}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/api/preview/<int:file_id>', methods=['GET'])
@require_auth
def api_preview_file(token_data, file_id):
    """Переглянути вміст файлу"""
    user_id = token_data['user_id']
    
    content_type, content, error = get_file_content(file_id, user_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    if content_type == 'text':
        return jsonify({'success': True, 'type': 'text', 'content': content}), 200
    
    elif content_type == 'image':
        # Для зображень повертаємо base64
        try:
            with open(content, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            return jsonify({'success': True, 'type': 'image', 'content': img_data}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Помилка читання зображення: {str(e)}'}), 500
    
    return jsonify({'success': False, 'message': 'Непідтримуваний тип'}), 400

@app.route('/api/download/<int:file_id>', methods=['GET'])
@require_auth
def api_download_file(token_data, file_id):
    """Завантажити файл"""
    user_id = token_data['user_id']
    
    filepath, error = download_file(file_id, user_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/delete/<int:file_id>', methods=['DELETE'])
@require_auth
def api_delete_file(token_data, file_id):
    """Видалити файл"""
    user_id = token_data['user_id']
    
    success, message = remove_file(file_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

# === ЗАПУСК СЕРВЕРА ===

if __name__ == '__main__':
    print("🚀 Запуск Flask сервера на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)