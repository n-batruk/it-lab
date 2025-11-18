[![Tests](https://github.com/n-batruk/it-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/n-batruk/it-lab/actions/workflows/tests.yml)

## Опис проєкту

Проєкт для управління файлами з веб- та десктоп-клієнтами.

## Встановлення

```bash
pip install -r requirements.txt
```

## Запуск тестів

```bash
pytest tests/ -v
```

## Структура проєкту

- `backend/` - Backend API на Flask
- `frontend/` - Веб-клієнт
- `desktop_client/` - Десктоп-клієнт
- `tests/` - Тести
```