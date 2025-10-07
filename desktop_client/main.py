import eel
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_client.sync import select_and_sync_folder as sync_func

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, '../frontend')
eel.init(os.path.abspath(frontend_dir))

@eel.expose
def select_and_sync_folder(token):
    return sync_func(token)

if __name__ == '__main__':

    try:
        eel.start('login.html', size=(1400, 900))
        print("Desktop Client: http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()