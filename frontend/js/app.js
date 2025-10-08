const API_URL = 'http://localhost:5000/api';
let currentSortOrder = 'desc';
let currentFilter = 'all';

window.addEventListener('load', () => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token || !username) {
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('usernameDisplay').textContent = username;
    loadFiles();
    
    initDragAndDrop();
});

async function loadFiles() {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/files?sort_by=created_at&sort_order=${currentSortOrder}&filter=${currentFilter}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayFiles(data.files);
        } else {
            showMessage('Помилка завантаження файлів', 'danger');
        }
    } catch (error) {
        showMessage('Помилка з\'єднання з сервером', 'danger');
    }
}

function displayFiles(files) {
    const tbody = document.getElementById('filesTable');
    
    if (files.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Немає файлів</td></tr>';
        return;
    }
    
    tbody.innerHTML = files.map(file => `
        <tr>
            <td>
                <a href="/* Загальні стилі */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Таблиця файлів */
.table-hover tbody tr:hover {
    cursor: pointer;
    background-color: #f8f9fa;
}

.table td, .table th {
    vertical-align: middle;
}

/* Область перегляду */
#previewArea {
    min-height: 300px;
    max-height: 600px;
    overflow-y: auto;" onclick="previewFile(${file.id}); return false;">
                    ${file.file_extension === '.c' ? '📄' : '🖼️'} ${file.filename}
                </a>
            </td>
            <td class="col-created">${formatDate(file.created_at)}</td>
            <td class="col-modified">${formatDate(file.modified_at)}</td>
            <td class="col-uploader">${file.uploaded_by || '-'}</td>
            <td class="col-editor">${file.edited_by || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="downloadFile(${file.id}, '${file.filename}')">⬇️</button>
                <button class="btn btn-sm btn-danger" onclick="deleteFile(${file.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('uk-UA');
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Оберіть файл', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Файл успішно завантажено', 'success');
            fileInput.value = '';
            loadFiles();
        } else {
            showMessage(data.message, 'danger');
        }
    } catch (error) {
        showMessage('Помилка завантаження файлу', 'danger');
    }
}

async function previewFile(fileId) {
    const token = localStorage.getItem('token');
    const previewArea = document.getElementById('previewArea');
    
    previewArea.innerHTML = '<div class="spinner-border" role="status"></div>';
    
    try {
        const response = await fetch(`${API_URL}/preview/${fileId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.type === 'text') {
                previewArea.innerHTML = `<pre class="text-start" style="max-height: 500px; overflow-y: auto; font-size: 12px;">${escapeHtml(data.content)}</pre>`;
            } else if (data.type === 'image') {
                previewArea.innerHTML = `<img src="data:image/jpeg;base64,${data.content}" class="img-fluid" alt="Preview">`;
            }
        } else {
            previewArea.innerHTML = `<p class="text-danger">${data.message}</p>`;
        }
    } catch (error) {
        previewArea.innerHTML = '<p class="text-danger">Помилка завантаження</p>';
    }
}

async function downloadFile(fileId, filename) {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/download/${fileId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            showMessage('Помилка завантаження файлу', 'danger');
        }
    } catch (error) {
        showMessage('Помилка завантаження файлу', 'danger');
    }
}

async function deleteFile(fileId) {
    if (!confirm('Ви впевнені, що хочете видалити цей файл?')) {
        return;
    }
    
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/delete/${fileId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Файл успішно видалено', 'success');
            loadFiles();
        } else {
            showMessage(data.message, 'danger');
        }
    } catch (error) {
        showMessage('Помилка видалення файлу', 'danger');
    }
}

function sortFiles(order) {
    currentSortOrder = order;
    loadFiles();
}

function filterFiles() {
    currentFilter = document.getElementById('filterSelect').value;
    loadFiles();
}

function toggleColumns() {
    const showCreated = document.getElementById('showCreated').checked;
    const showModified = document.getElementById('showModified').checked;
    const showUploader = document.getElementById('showUploader').checked;
    const showEditor = document.getElementById('showEditor').checked;
    
    document.querySelectorAll('.col-created').forEach(el => {
        el.style.display = showCreated ? '' : 'none';
    });
    
    document.querySelectorAll('.col-modified').forEach(el => {
        el.style.display = showModified ? '' : 'none';
    });
    
    document.querySelectorAll('.col-uploader').forEach(el => {
        el.style.display = showUploader ? '' : 'none';
    });
    
    document.querySelectorAll('.col-editor').forEach(el => {
        el.style.display = showEditor ? '' : 'none';
    });
}

async function syncFolder() {
    if (typeof eel === 'undefined' || typeof eel.select_and_sync_folder !== 'function') {
        showMessage('Синхронізація доступна тільки в десктоп-версії', 'secondary');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            showMessage('Спочатку увійдіть у систему', 'secondary');
            return;
        }
        
        showMessage('Виберіть папку для синхронізації...', 'secondary');
        
        const result = await eel.select_and_sync_folder(token)();
        
        if (result && result.message) {
            showMessage(result.message, result.success ? 'success' : 'secondary');
        } else {
            showMessage('Синхронізація завершена', 'success');
        }
        
        setTimeout(() => loadFiles(), 1000);
    } catch (error) {
        console.error('Помилка синхронізації:', error);
        showMessage('Помилка синхронізації папки', 'danger');
    }
}
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    window.location.href = 'login.html';
}

function showMessage(message, type) {
    const messageArea = document.getElementById('messageArea');
    messageArea.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    setTimeout(() => {
        messageArea.innerHTML = '';
    }, 5000);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}