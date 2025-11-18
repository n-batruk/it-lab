[![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/tests.yml)

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

Важливо: замініть `YOUR_USERNAME` та `YOUR_REPO` на ваші значення GitHub.

## Особливості конфігурації:

1. Матриця ОС: Ubuntu, Windows, macOS
2. Матриця Python: 3.9, 3.10, 3.11
3. Кешування: pip-кеш через `actions/setup-python@v5` та додатковий кеш через `actions/cache@v4`
4. Артефакти: зберігаються результати тестів у форматі JUnit XML
5. Запуск: на push та pull_request до main

Після створення файлів та push до репозиторію GitHub Actions автоматично запустить тести на всіх ОС.

