# YaCut — сервис коротких ссылок

YaCut — это веб-приложение на Flask, позволяющее создавать короткие ссылки для любых URL-адресов.  
Пользователь может сгенерировать случайный идентификатор или задать свой вариант короткого имени.

---

## Возможности

- Создание коротких ссылок через веб-интерфейс  
- Создание коротких ссылок через API  
- Проверка пользовательских идентификаторов на корректность и уникальность  
- Перенаправление по короткому идентификатору на исходный URL  
- Простая и надёжная работа с базой данных SQLite

---

## Технологии

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Jinja2
- SQLite (по умолчанию)

---

## Установка и запуск

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/ArtemYuvanov/async-yacut-master.git
   cd async-yacut-master
   ```
2. Установите и активируйте виртуальное окружение:
   ```
   python -m venv venv
   source venv/Scripts/activate      # Windows
   source venv/bin/activate          # macOS/Linux
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
4. Создайте файл .env и добавьте настройки:
   ```
   FLASK_APP=yacut
   FLASK_ENV=development
   SECRET_KEY=super_secret_key
   DATABASE_URI=sqlite:///db.sqlite3
   ```
5. Инициализируйте базу данных:
   ```
   flask db upgrade
   ```
6. Запустите сервер:
   ```
   flask run
   ```

Приложение будет доступно по адресу:
[YaCut](http://127.0.0.1:5000)

## Документация API

-**Файл спецификации API**
[openapi.yml](https://github.com/ArtemYuvanov/async-yacut-master/blob/master/openapi.yml)

## Структура проекта

yacut/
├── __init__.py
├── api_views.py         # API эндпоинты
├── async_views.py       # Ассинхронная загрузка файлов
├── constants.py         # Константы проекта
├── error_handlers.py    # Кастомные обработчики ошибок API
├── forms.py             # Flask-WTF формы
├── models.py            # SQLAlchemy модель URLMap
├── static/              # Статические файлы (CSS, JS)
├── templates/           # HTML-шаблоны (index.html и др.)
├── .py             # Утилиты (генерация коротких id)
└── views.py             # Основные маршруты сайта


## Автор

Артём Юванов
[GitHub](https://github.com/ArtemYuvanov)

Проект создан в рамках учебного курса Flask + API
