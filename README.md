# Secure Messenger

Защищенный мессенджер с веб и мобильным интерфейсом, построенный на Flask и KivyMD.

## Возможности

- Регистрация и авторизация пользователей
- Защищенный обмен сообщениями
- Веб и мобильный интерфейс
- Темная тема
- Реальное время обновления сообщений

## Технологии

- **Бэкенд**: Flask, SQLAlchemy, JWT
- **Веб-интерфейс**: HTML, CSS, JavaScript
- **Мобильное приложение**: KivyMD
- **База данных**: SQLite
- **Безопасность**: bcrypt, JWT tokens

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/secure-messenger.git
cd secure-messenger
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл .env и настройте переменные окружения:
```bash
SECRET_KEY=your-secret-key
API_URL=http://localhost:5000
```

4. Запустите сервер:
```bash
python server.py
```

5. Запустите клиент:
```bash
python main.py
```

## Структура проекта

- `server.py` - Flask сервер
- `main.py` - KivyMD мобильное приложение
- `templates/` - HTML шаблоны
- `static/` - CSS стили и статические файлы
- `requirements.txt` - зависимости проекта

## Лицензия

MIT
