import os
import requests
from tkinter import filedialog, Tk

API_URL = 'http://localhost:5000/api'

def upload_file_to_server(file_path, token):
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

def sync_files_to_server(files_list, token):
    results = {
        'total': len(files_list),
        'uploaded': 0,
        'failed': 0,
        'errors': []
    }
    
    for file_path in files_list:
        file_name = os.path.basename(file_path)
        success, message = upload_file_to_server(file_path, token)
        
        if success:
            results['uploaded'] += 1
            print(f"Done: {file_name}")
        else:
            results['failed'] += 1
            results['errors'].append(f"{file_name}: {message}")
            print(f"Error: {file_name}: {message}")
    
    return results

def select_and_sync_folder(token):
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title='Оберіть папку для синхронізації')
    root.destroy()

    if not folder_path:
        print(" Папку не обрано")
        return {'success': False, 'message': 'Папку не обрано'}

    print(f"Chosen folder: {folder_path}")

    files_to_upload = []
    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            files_to_upload.append(os.path.join(root_dir, file))

    if not files_to_upload:
        print("У папці немає файлів для синхронізації")
        return {'success': False, 'message': 'У папці немає файлів'}

    print(f"📤 Знайдено {len(files_to_upload)} файлів. Починаю синхронізацію...")

    results = sync_files_to_server(files_to_upload, token)

    print("\n📊 РЕЗУЛЬТАТ СИНХРОНІЗАЦІЇ:")
    print(f"  Всього файлів: {results['total']}")
    print(f"  Завантажено: {results['uploaded']}")
    print(f"  Помилок: {results['failed']}")
    if results['errors']:
        for e in results['errors']:
            print("  ❌", e)
    
    message = f"Синхронізовано {results['uploaded']}/{results['total']} файлів"
    if results['failed'] > 0:
        message += f" (помилок: {results['failed']})"
    
    return {
        'success': results['failed'] == 0,
        'message': message,
        'results': results
    }