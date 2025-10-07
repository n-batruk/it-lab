import os
import sys
from flask import Flask, render_template, redirect, url_for

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

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


if __name__ == '__main__':

    print("Web Client: http://localhost:3000")
    
    app.run(debug=True, host='0.0.0.0', port=3000)