import os
import requests
from tkinter import filedialog, Tk

API_URL = 'http://localhost:5000/api'

def select_and_sync_folder(token):
    """Вибрати папку та синхронізувати її з сервером"""
    from tkinter import filedialog, Tk

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title='Оберіть папку для синхронізації')
    root.destroy()

    if not folder_path:
        print("❌ Папку не обрано")
        return

    print(f"📁 Обрана папка: {folder_path}")

    # Перевірка наявності файлів
    files_to_upload = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.c', '.jpg', '.jpeg')):
                files_to_upload.append(os.path.join(root, file))

    if not files_to_upload:
        print("⚠️ У папці немає файлів .c або .jpg для синхронізації")
        return

    print(f"📤 Знайдено {len(files_to_upload)} файлів. Починаю синхронізацію...")

    # Синхронізація
    results = sync_folder_with_server(folder_path, token)

    print("\n📊 РЕЗУЛЬТАТ СИНХРОНІЗАЦІЇ:")
    print(f"  Всього файлів: {results['total']}")
    print(f"  Завантажено: {results['uploaded']}")
    print(f"  Помилок: {results['failed']}")
    if results['errors']:
        for e in results['errors']:
            print("  ❌", e)



def upload_file_to_server(file_path, token):
    """Завантажити файл на сервер"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f'{API_URL}/upload',
                files=files,
                headers=headers
            )
            
            if response.status_code == 201:
                return True, 'Успішно завантажено'
            else:
                return False, response.json().get('message', 'Помилка')
    except Exception as e:
        return False, str(e)

def sync_folder_with_server(folder_path, token):
    """Синхронізувати всю папку з сервером"""
    results = {
        'total': 0,
        'uploaded': 0,
        'failed': 0,
        'errors': []
    }
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.c', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                results['total'] += 1
                
                success, message = upload_file_to_server(file_path, token)
                
                if success:
                    results['uploaded'] += 1
                    print(f"✅ {file}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{file}: {message}")
                    print(f"❌ {file}: {message}")
    
    return results