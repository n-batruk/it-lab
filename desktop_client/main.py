import eel
import os
import sys

# Додати backend до шляху для імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Імпорт функції синхронізації
from desktop_client.sync import select_and_sync_folder

# Ініціалізація Eel зі спільною папкою frontend
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, '../frontend')
eel.init(os.path.abspath(frontend_dir))

# Експонуємо функцію синхронізації для JavaScript
@eel.expose
def select_and_sync_folder(token):
    """Викликається з JavaScript для синхронізації папки"""
    from desktop_client.sync import select_and_sync_folder as sync
    return sync(token)

if __name__ == '__main__':
    print("🚀 Запуск Desktop Client...")
    print("📂 Використовується спільний інтерфейс з папки frontend/")
    
    # Запуск Eel
    try:
        eel.start('login.html', size=(1400, 900), position=(100, 100))
    except Exception as e:
        print(f"❌ Помилка запуску: {e}")
        print("⚠️ Переконайтесь, що Flask сервер запущений на http://localhost:5000")