import os
import sys
from flask import Flask, render_template, redirect, url_for

# Додати backend до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Шлях до спільної папки frontend
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

# Створення Flask додатку зі спільними папками
app = Flask(__name__,
            template_folder=FRONTEND_PATH,
            static_folder=FRONTEND_PATH,
            static_url_path='')

# === ROUTES ===

@app.route('/')
def home():
    """Головна сторінка - перенаправлення на логін або дашборд"""
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Сторінка входу"""
    return render_template('login.html')

@app.route('/register')
def register():
    """Сторінка реєстрації"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Головна сторінка з файлами"""
    return render_template('index.html')

# === ЗАПУСК ===

if __name__ == '__main__':
    print("🌐 Запуск Web Client...")
    print(f"📂 Використовується спільний інтерфейс з папки: {FRONTEND_PATH}")
    print("🔗 Відкрийте браузер: http://localhost:3000")
    print("⚠️ Переконайтесь, що Backend сервер запущений на http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=3000)